from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import path
from django.contrib import admin
from django.views.decorators.http import require_POST
from .models import Notification


# ── VIEWS ─────────────────────────────────────────────────────────────────────

@login_required
def notification_list_view(request):
    """Barcha bildirishnomalar sahifasi"""
    filter_type = request.GET.get('type', '')
    notifications = Notification.objects.filter(recipient=request.user)

    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type:
        notifications = notifications.filter(notif_type=filter_type)

    # Sahifaga kirishda ko'rilmagan soni
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    return render(request, 'notifications/list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
        'filter_type': filter_type,
        'type_choices': Notification.TYPE_CHOICES,
    })


@login_required
def notification_read_view(request, pk):
    """Bildirishnomani o'qilgan deb belgilash va havolaga yo'naltirish"""
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.mark_read()
    if notif.link:
        return redirect(notif.link)
    return redirect('notification_list')


@login_required
@require_POST
def mark_all_read_view(request):
    """Hammasini o'qilgan deb belgilash"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return redirect('notification_list')


@login_required
@require_POST
def notification_delete_view(request, pk):
    """Bitta bildirishnomani o'chirish"""
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.delete()
    return redirect('notification_list')


@login_required
@require_POST
def delete_all_read_view(request):
    """O'qilganlarni tozalash"""
    Notification.objects.filter(recipient=request.user, is_read=True).delete()
    return redirect('notification_list')


@login_required
def unread_count_api(request):
    """AJAX — o'qilmagan bildirishnomalar soni"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def recent_notifications_api(request):
    """AJAX — so'nggi 8 ta bildirishnoma (navbar dropdown uchun)"""
    notifs = Notification.objects.filter(recipient=request.user)[:8]
    data = [{
        'id':         n.pk,
        'icon':       n.icon,
        'title':      n.title,
        'message':    n.message[:80],
        'link':       f'/notifications/{n.pk}/read/',
        'is_read':    n.is_read,
        'time':       n.created_at.strftime('%d %b, %H:%M'),
        'type':       n.notif_type,
    } for n in notifs]
    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'notifications': data, 'unread': unread})


# ── URLS ──────────────────────────────────────────────────────────────────────

urlpatterns = [
    path('',                       notification_list_view,    name='notification_list'),
    path('<int:pk>/read/',         notification_read_view,    name='notification_read'),
    path('<int:pk>/delete/',       notification_delete_view,  name='notification_delete'),
    path('mark-all-read/',         mark_all_read_view,        name='notification_mark_all'),
    path('delete-read/',           delete_all_read_view,      name='notification_delete_read'),
    path('api/count/',             unread_count_api,          name='notification_count_api'),
    path('api/recent/',            recent_notifications_api,  name='notification_recent_api'),
]


# ── ADMIN ─────────────────────────────────────────────────────────────────────

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['recipient', 'notif_type', 'title', 'is_read', 'created_at']
    list_filter   = ['notif_type', 'is_read']
    search_fields = ['recipient__username', 'title']
    list_editable = ['is_read']
    actions       = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, "Belgilangan bildirishnomalar o'qilgan deb belgilandi.")
    mark_as_read.short_description = "O'qilgan deb belgilash"
