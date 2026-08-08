from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from apps.accounts.models import User
from .models import Conversation, Message


@login_required
def inbox_view(request):
    """Barcha suhbatlar ro'yxati"""
    conversations = request.user.conversations.prefetch_related(
        'participants', 'messages'
    ).order_by('-updated_at')

    # Har bir suhbat uchun qo'shimcha ma'lumot
    conv_data = []
    total_unread = 0
    for conv in conversations:
        other = conv.other_participant(request.user)
        last  = conv.last_message()
        unread = conv.unread_count(request.user)
        total_unread += unread
        conv_data.append({
            'conv': conv,
            'other': other,
            'last': last,
            'unread': unread,
        })

    return render(request, 'messaging/inbox.html', {
        'conv_data': conv_data,
        'total_unread': total_unread,
    })


@login_required
def conversation_view(request, conv_id):
    """Bitta suhbat ko'rinishi"""
    conv = get_object_or_404(Conversation, pk=conv_id, participants=request.user)
    other = conv.other_participant(request.user)

    # Xabarlarni o'qilgan deb belgilash
    conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    msgs = conv.messages.select_related('sender').all()

    # Sidebar uchun barcha suhbatlar
    conversations = request.user.conversations.prefetch_related(
        'participants', 'messages'
    ).order_by('-updated_at')
    
    conv_data = []
    total_unread = 0
    for c in conversations:
        c_other = c.other_participant(request.user)
        c_last  = c.last_message()
        c_unread = c.unread_count(request.user)
        total_unread += c_unread
        conv_data.append({
            'conv': c,
            'other': c_other,
            'last': c_last,
            'unread': c_unread,
        })

    # Foydalanuvchi yuborgan oxirgi o'qilgan xabar ID sini topish
    last_read_id = 0
    last_read_msg = conv.messages.filter(sender=request.user, is_read=True).order_by('-pk').first()
    if last_read_msg:
        last_read_id = last_read_msg.pk

    return render(request, 'messaging/conversation.html', {
        'conv': conv,
        'other': other,
        'chat_messages': msgs,
        'conv_data': conv_data,
        'total_unread': total_unread,
        'last_read_id': last_read_id,
    })


@login_required
def start_conversation_view(request, username):
    """Yangi suhbat boshlash yoki mavjudiga o'tish"""
    other = get_object_or_404(User, username=username)
    if other == request.user:
        django_messages.error(request, "O'zingizga xabar yubora olmaysiz.")
        return redirect('profile', username=username)

    conv = Conversation.get_or_create_between(request.user, other)
    return redirect('conversation', conv_id=conv.pk)


@login_required
@require_POST
def send_message_view(request, conv_id):
    """Xabar yuborish (matn va fayl bilan)"""
    conv = get_object_or_404(Conversation, pk=conv_id, participants=request.user)
    content = request.POST.get('content', '').strip()
    attachment = request.FILES.get('attachment')

    if not content and not attachment:
        return JsonResponse({'error': 'Xabar bo\'sh bo\'lishi mumkin emas'}, status=400)

    msg = Message.objects.create(
        conversation=conv,
        sender=request.user,
        content=content,
        attachment=attachment
    )
    conv.save() # updated_at yangilanadi

    # Bildirishnoma
    other = conv.other_participant(request.user)
    if other:
        try:
            from apps.notifications.service import notify
            notify(
                recipient=other,
                sender=request.user,
                notif_type='mention',
                title=f"{request.user.username} sizga xabar yubordi",
                message=content[:80] if content else "Fayl yuborildi",
                link=f'/messages/{conv.pk}/',
            )
        except Exception:
            pass

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
              request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    # WebSocket Broadcast
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{conv.pk}',
            {
                'type': 'chat_message',
                'data': {
                    'id':      msg.pk,
                    'content': msg.content,
                    'sender':  msg.sender.username,
                    'time':    msg.created_at.strftime('%H:%M'),
                    'is_mine': False, # Qabul qiluvchi uchun bu har doim False
                    'attachment_url':  msg.attachment.url if msg.attachment else None,
                    'attachment_name': msg.attachment.name.split('/')[-1] if msg.attachment else None,
                    'is_image': msg.is_image,
                    'is_video': msg.is_video,
                }
            }
        )
    except Exception as e:
        print(f"WebSocket broadcast error: {e}")

    if is_ajax:
        return JsonResponse({
            'id':      msg.pk,
            'content': msg.content,
            'sender':  msg.sender.username,
            'time':    msg.created_at.strftime('%H:%M'),
            'is_mine': True,
            'attachment_url':  msg.attachment.url if msg.attachment else None,
            'attachment_name': msg.attachment.name.split('/')[-1] if msg.attachment else None,
            'is_image': msg.is_image,
            'is_video': msg.is_video,
        })
    return redirect('conversation', conv_id=conv.pk)


@login_required
def poll_messages_view(request, conv_id):
    """AJAX — yangi xabarlarni olish va o'qilganlik holatini tekshirish"""
    conv = get_object_or_404(Conversation, pk=conv_id, participants=request.user)
    last_id = int(request.GET.get('last_id', 0))
    new_msgs = conv.messages.filter(pk__gt=last_id).select_related('sender')

    # Yangi kelgan xabarlarni o'qilgan deb belgilash
    new_msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # Foydalanuvchi yuborgan oxirgi o'qilgan xabar ID sini topish
    last_read_id = 0
    last_read_msg = conv.messages.filter(sender=request.user, is_read=True).order_by('-pk').first()
    if last_read_msg:
        last_read_id = last_read_msg.pk

    return JsonResponse({
        'messages': [
            {
                'id':      m.pk,
                'content': m.content,
                'sender':  m.sender.username,
                'time':    m.created_at.strftime('%H:%M'),
                'is_mine': m.sender == request.user,
                'attachment_url':  m.attachment.url if m.attachment else None,
                'attachment_name': m.attachment.name.split('/')[-1] if m.attachment else None,
                'is_image': m.is_image,
                'is_video': m.is_video,
            } for m in new_msgs
        ],
        'last_read_id': last_read_id
    })


@login_required
def unread_count_api(request):
    """AJAX — o'qilmagan xabarlar soni"""
    count = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    return JsonResponse({'count': count})


@login_required
def user_search_api(request):
    """AJAX — foydalanuvchilarni username bo'yicha qidirish"""
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse({'users': []})

    users = User.objects.filter(
        Q(username__icontains=q) | Q(display_name__icontains=q)
    ).exclude(pk=request.user.pk).order_by('username')[:15]

    results = []
    for u in users:
        avatar_url = u.avatar.url if u.avatar else None
        results.append({
            'username':     u.username,
            'display_name': getattr(u, 'display_name', '') or u.username,
            'avatar':       avatar_url,
            'chat_url':     f'/messages/start/{u.username}/',
            'profile_url':  f'/profile/{u.username}/',
        })
    return JsonResponse({'users': results})
