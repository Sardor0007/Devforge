# apps/jams/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count
from django.views.decorators.http import require_POST

from .models import Jam, JamSubmission


def jam_list(request):
    """Barcha game jam'lar ro'yxati"""
    now = timezone.now()

    active_jams = Jam.objects.filter(
        is_active=True, end_date__gte=now
    ).annotate(submission_count=Count('submissions')).order_by('end_date')

    past_jams = Jam.objects.filter(
        is_active=True, end_date__lt=now
    ).annotate(submission_count=Count('submissions')).order_by('-end_date')[:6]

    user_submissions = {}
    if request.user.is_authenticated:
        for sub in JamSubmission.objects.filter(creator=request.user):
            user_submissions[sub.jam_id] = sub

    return render(request, 'jams/list.html', {
        'active_jams': active_jams,
        'past_jams': past_jams,
        'user_submissions': user_submissions,
        'now': now,
    })


def jam_detail(request, pk):
    """Bitta jam tafsiloti va uning submissions'lari"""
    jam = get_object_or_404(Jam, pk=pk)
    submissions = jam.submissions.select_related('creator').order_by('-votes', '-created_at')

    user_submission = None
    if request.user.is_authenticated:
        user_submission = submissions.filter(creator=request.user).first()

    return render(request, 'jams/detail.html', {
        'jam': jam,
        'submissions': submissions,
        'user_submission': user_submission,
        'now': timezone.now(),
    })


@login_required
def jam_create(request):
    """Yangi game jam yaratish (faqat admin yoki Gold/Platinum foydalanuvchilar)"""
    if not (request.user.is_staff or request.user.subscription_type in ['gold', 'platinum']):
        messages.error(request, "Game Jam yaratish uchun Gold yoki Platinum obuna kerak.")
        return redirect('jams:list')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        theme = request.POST.get('theme', '').strip()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if not all([title, description, start_date, end_date]):
            messages.error(request, "Barcha majburiy maydonlarni to'ldiring.")
        else:
            jam = Jam.objects.create(
                title=title,
                description=description,
                theme=theme,
                start_date=start_date,
                end_date=end_date,
                created_by=request.user,
            )
            messages.success(request, f"✅ '{jam.title}' game jam muvaffaqiyatli yaratildi!")
            return redirect('jams:detail', pk=jam.pk)

    return render(request, 'jams/create.html')


@login_required
def jam_submit(request, pk):
    """Game jam'ga loyiha topshirish"""
    jam = get_object_or_404(Jam, pk=pk, is_active=True)
    now = timezone.now()

    if now < jam.start_date:
        messages.error(request, "Jam hali boshlanmagan.")
        return redirect('jams:detail', pk=pk)

    if now > jam.end_date:
        messages.error(request, "Jam tugagan. Yangi topshiriq qabul qilinmaydi.")
        return redirect('jams:detail', pk=pk)

    # Foydalanuvchi allaqachon topshirganmi?
    if JamSubmission.objects.filter(jam=jam, creator=request.user).exists():
        messages.info(request, "Siz allaqachon bu jam'ga topshiriq yuborgansiz.")
        return redirect('jams:detail', pk=pk)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        demo_url = request.POST.get('demo_url', '').strip()
        file = request.FILES.get('file')

        if not title:
            messages.error(request, "Topshiriq sarlavhasi majburiy.")
        elif not file and not demo_url:
            messages.error(request, "Fayl yoki Demo URL majburiy.")
        else:
            JamSubmission.objects.create(
                jam=jam,
                creator=request.user,
                title=title,
                description=description,
                demo_url=demo_url,
                file=file,
            )
            messages.success(request, f"🎮 '{title}' muvaffaqiyatli topshirildi!")
            return redirect('jams:detail', pk=pk)

    return render(request, 'jams/submit.html', {'jam': jam})


@login_required
@require_POST
def jam_vote(request, pk):
    """AJAX — submission'ga ovoz berish"""
    submission = get_object_or_404(JamSubmission, pk=pk)

    # O'z topshirig'iga ovoz bera olmaydi
    if submission.creator == request.user:
        return JsonResponse({'error': "O'z topshirig'ingizga ovoz bera olmaysiz."}, status=400)

    # Jam aktiv bo'lishi kerak
    if not submission.jam.is_active:
        return JsonResponse({'error': "Bu jam yakunlangan."}, status=400)

    submission.votes += 1
    submission.save(update_fields=['votes'])

    return JsonResponse({'votes': submission.votes, 'ok': True})
