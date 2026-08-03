from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import SkillTest, TestQuestion, SkillCertificate, TestAttempt


def assessment_list(request):
    """Barcha mavjud testlar ro'yxati"""
    tests = SkillTest.objects.filter(is_active=True).prefetch_related('questions')
    user_certs = {}
    if request.user.is_authenticated:
        for cert in SkillCertificate.objects.filter(user=request.user):
            user_certs[cert.skill_test_id] = cert
    return render(request, 'assessment/list.html', {
        'tests': tests,
        'user_certs': user_certs,
    })


@login_required
def assessment_detail(request, pk):
    """Test haqida ma'lumot va boshlash tugmasi"""
    test = get_object_or_404(SkillTest, pk=pk, is_active=True)
    certificate = SkillCertificate.objects.filter(
        user=request.user, skill_test=test
    ).first()
    attempts = TestAttempt.objects.filter(
        user=request.user, skill_test=test
    ).order_by('-started_at')[:5]
    return render(request, 'assessment/detail.html', {
        'test': test,
        'certificate': certificate,
        'attempts': attempts,
    })


@login_required
def assessment_start(request, pk):
    """Testni boshlash — savollarni yuklaydi"""
    test = get_object_or_404(SkillTest, pk=pk, is_active=True)

    # Agar allaqachon o'tgan bo'lsa qayta urinib bo'lmaydi (passed)
    passed = SkillCertificate.objects.filter(
        user=request.user, skill_test=test, passed=True
    ).exists()
    if passed:
        messages.info(request, "Siz bu testdan allaqachon muvaffaqiyatli o'tgansiz! 🎉")
        return redirect('assessment_detail', pk=pk)

    # Attempt yaratish yoki topish
    attempt, created = TestAttempt.objects.get_or_create(
        user=request.user,
        skill_test=test,
        finished=False,
        defaults={'answers': {}}
    )

    questions = test.questions.all()
    return render(request, 'assessment/exam.html', {
        'test': test,
        'questions': questions,
        'attempt': attempt,
        'time_limit_seconds': test.time_limit * 60,
    })


@login_required
@require_POST
def assessment_submit(request, pk):
    """Test javoblarini qabul qilish va natijani hisoblash"""
    test = get_object_or_404(SkillTest, pk=pk, is_active=True)
    attempt = get_object_or_404(
        TestAttempt, user=request.user, skill_test=test, finished=False
    )

    questions = test.questions.all()
    correct_count = 0
    total = questions.count()

    for q in questions:
        submitted = request.POST.get(f'q_{q.pk}', '').lower()
        if submitted == q.correct:
            correct_count += 1

    score = round((correct_count / total) * 100) if total > 0 else 0
    passed = score >= test.passing_score

    # Attempt tugatish
    attempt.finished = True
    attempt.save()

    # Sertifikat yaratish/yangilash
    cert, created = SkillCertificate.objects.get_or_create(
        user=request.user,
        skill_test=test,
        defaults={'score': score, 'passed': passed}
    )
    if not created:
        cert.score = score
        cert.passed = passed
        cert.issued_at = timezone.now()
        cert.save()

    if passed:
        # XP berish
        request.user.add_xp(test.xp_reward)
        # Badge berish
        if test.badge_reward:
            from apps.accounts.models import UserBadge
            UserBadge.objects.get_or_create(
                user=request.user, badge=test.badge_reward
            )
        # Bildirishnoma
        try:
            from apps.notifications.service import send_notification
            send_notification(
                recipient=request.user,
                sender=None,
                notif_type='system',
                title=f"🎓 {test.skill_name} sertifikati olindi!",
                message=f"Siz {score}% natija bilan testdan muvaffaqiyatli o'tdingiz.",
                link=f'/assessment/{pk}/'
            )
        except Exception:
            pass
        messages.success(request, f"🎉 Tabriklaymiz! {score}% natija — Sertifikat olindi!")
    else:
        messages.warning(request, f"😔 {score}% — O'tish uchun {test.passing_score}% kerak. Qayta urining!")

    return redirect('assessment_result', pk=pk)


@login_required
def assessment_result(request, pk):
    """Natija sahifasi"""
    test = get_object_or_404(SkillTest, pk=pk)
    cert = get_object_or_404(SkillCertificate, user=request.user, skill_test=test)
    return render(request, 'assessment/result.html', {
        'test': test,
        'cert': cert,
    })
