from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from .models import Challenge, ChallengeParticipant


def challenges_list(request):
    """Barcha aktiv challengelar"""
    now = timezone.now()
    challenges = Challenge.objects.filter(
        is_active=True, end_date__gt=now
    ).order_by('end_date')

    user_progress = {}
    if request.user.is_authenticated:
        for p in ChallengeParticipant.objects.filter(user=request.user):
            user_progress[p.challenge_id] = p

    return render(request, 'challenges/list.html', {
        'challenges': challenges,
        'user_progress': user_progress,
        'now': now,
    })


@login_required
def challenge_join(request, pk):
    """Challenge'ga qo'shilish"""
    challenge = get_object_or_404(Challenge, pk=pk, is_active=True)
    now = timezone.now()
    if now > challenge.end_date:
        messages.error(request, "Bu challenge tugagan.")
        return redirect('challenges_list')

    _, created = ChallengeParticipant.objects.get_or_create(
        challenge=challenge, user=request.user
    )
    if created:
        messages.success(request, f"✅ '{challenge.title}' challenge'ga qo'shildingiz!")
    else:
        messages.info(request, "Siz allaqachon bu challenge'da qatnashyapsiz.")
    return redirect('challenges_list')


@login_required
def my_challenges(request):
    """Foydalanuvchi qatnashayotgan challengelar"""
    participations = ChallengeParticipant.objects.filter(
        user=request.user
    ).select_related('challenge').order_by('-joined_at')
    return render(request, 'challenges/my.html', {
        'participations': participations,
    })


@login_required
def challenge_progress_api(request, pk):
    """AJAX — foydalanuvchi progress'ini qaytaradi"""
    challenge = get_object_or_404(Challenge, pk=pk)
    try:
        p = ChallengeParticipant.objects.get(user=request.user, challenge=challenge)
        return JsonResponse({
            'current': p.current_count,
            'target': challenge.target_count,
            'completed': p.completed,
            'percent': min(100, round(p.current_count / challenge.target_count * 100))
        })
    except ChallengeParticipant.DoesNotExist:
        return JsonResponse({'joined': False})


def challenge_detail(request, pk):
    """Challenge tafsiloti — top qatnashuvchilar va progress"""
    challenge = get_object_or_404(Challenge, pk=pk, is_active=True)

    # Top 20 qatnashuvchi
    top_participants = ChallengeParticipant.objects.filter(
        challenge=challenge
    ).select_related('user').order_by('-current_count', '-completed', 'joined_at')[:20]

    user_participation = None
    if request.user.is_authenticated:
        try:
            user_participation = ChallengeParticipant.objects.get(
                challenge=challenge, user=request.user
            )
        except ChallengeParticipant.DoesNotExist:
            pass

    return render(request, 'challenges/detail.html', {
        'challenge': challenge,
        'top_participants': top_participants,
        'user_participation': user_participation,
        'now': timezone.now(),
    })

