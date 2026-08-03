"""
DevForge — Celery Background Tasks
Foydalanish:
    from apps.tasks import send_notification_email, auto_approve_deliveries
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


# ── EMAIL TASKS ───────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_email(self, recipient_email, subject, message, html_message=None):
    """
    Foydalanuvchiga email yuborish (background).
    Celery worker tomonidan asinxron bajariladi.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient_email}: {subject}")
        return {"status": "sent", "recipient": recipient_email}
    except Exception as exc:
        logger.error(f"Email failed to {recipient_email}: {exc}")
        raise self.retry(exc=exc)


@shared_task
def send_welcome_email(user_id):
    """Yangi foydalanuvchiga xush kelibsiz emaili"""
    from apps.accounts.models import User
    try:
        user = User.objects.get(pk=user_id)
        subject = "DevForge'ga xush kelibsiz! 🎮"
        message = f"""Salom {user.username}!

DevForge platformasiga xush kelibsiz!

Platformamizda siz:
- O'yin loyihalarini boshqarishingiz
- Jamoangiz bilan ishlashingiz
- 3D Studio'dan foydalanishingiz
- Kurs va darslardan o'rganishingiz mumkin.

Boshlash uchun: {settings.SITE_NAME}

Hurmat bilan,
{settings.SITE_NAME} jamoasi
"""
        send_notification_email.delay(user.email, subject, message)
        logger.info(f"Welcome email queued for {user.email}")
    except Exception as e:
        logger.error(f"send_welcome_email error: {e}")


@shared_task
def send_job_notification_email(job_id, event_type):
    """
    Ish e'loni hodisalari uchun email:
    event_type: 'proposal_accepted' | 'escrow_funded' | 'delivery_submitted' | 'delivery_approved'
    """
    from apps.jobs.models import Job
    try:
        job = Job.objects.select_related('client', 'selected_worker').get(pk=job_id)

        if event_type == 'proposal_accepted' and job.selected_worker:
            subject = f"Tabriklaymiz! '{job.title}' ishi uchun tanlandingiz"
            message = (
                f"Salom {job.selected_worker.username}!\n\n"
                f"'{job.title}' loyihasida ishlash uchun siz tanlandingiz.\n"
                f"Mijoz to'lovni amalga oshirishi bilan ish boshlashingiz mumkin.\n\n"
                f"Hurmat bilan, {settings.SITE_NAME}"
            )
            send_notification_email.delay(job.selected_worker.email, subject, message)

        elif event_type == 'escrow_funded' and job.selected_worker:
            subject = f"To'lov amalga oshirildi — '{job.title}'"
            message = (
                f"Salom {job.selected_worker.username}!\n\n"
                f"Mijoz escrow'ga to'lovni amalga oshirdi. Endi ishni boshlashingiz mumkin!\n\n"
                f"Hurmat bilan, {settings.SITE_NAME}"
            )
            send_notification_email.delay(job.selected_worker.email, subject, message)

        elif event_type == 'delivery_submitted':
            subject = f"Ish topshirildi — '{job.title}'"
            message = (
                f"Salom {job.client.username}!\n\n"
                f"Ishchi ish natijasini yubordi. Ko'rib chiqing va tasdiqlang.\n\n"
                f"Hurmat bilan, {settings.SITE_NAME}"
            )
            send_notification_email.delay(job.client.email, subject, message)

        elif event_type == 'delivery_approved' and job.selected_worker:
            subject = f"Ish tasdiqlandi — '{job.title}'"
            message = (
                f"Salom {job.selected_worker.username}!\n\n"
                f"Ishing tasdiqlandi. Pul balansingizga o'tkazildi!\n\n"
                f"Hurmat bilan, {settings.SITE_NAME}"
            )
            send_notification_email.delay(job.selected_worker.email, subject, message)

    except Exception as e:
        logger.error(f"send_job_notification_email error (job={job_id}, event={event_type}): {e}")


# ── AUTO-APPROVAL TASK ────────────────────────────────────────────────────────

@shared_task
def auto_approve_old_deliveries():
    """
    3 kundan oshgan topshirilgan ishlarni avtomatik tasdiqlash.
    Celery Beat bilan har soat ishga tushirish kerak:
        CELERY_BEAT_SCHEDULE = {
            'auto-approve': {
                'task': 'apps.tasks.auto_approve_old_deliveries',
                'schedule': crontab(hour='*/1'),
            }
        }
    """
    from apps.jobs.models import Job
    from apps.notifications.service import notify_delivery_approved

    cutoff = timezone.now() - timezone.timedelta(days=3)
    jobs = Job.objects.filter(status='submitted').prefetch_related('deliveries')
    approved_count = 0

    for job in jobs:
        last_delivery = job.deliveries.order_by('-created_at').first()
        if last_delivery and last_delivery.created_at <= cutoff:
            # Escrow ni chiqarish
            try:
                escrow = job.escrow
                escrow.status = 'released'
                escrow.save()

                # Workerga to'lov
                if job.selected_worker:
                    worker_amount = escrow.amount - escrow.platform_fee
                    job.selected_worker.balance += worker_amount
                    job.selected_worker.save(update_fields=['balance'])

                job.status = 'approved'
                job.save(update_fields=['status'])
                job.deliveries.all().update(is_downloadable=True)

                # Bildirishnoma
                notify_delivery_approved(job)
                send_job_notification_email.delay(job.pk, 'delivery_approved')
                approved_count += 1
                logger.info(f"Auto-approved job #{job.pk}: {job.title}")
            except Exception as e:
                logger.error(f"Auto-approve error for job #{job.pk}: {e}")

    return {"approved": approved_count}


# ── WORKSPACE SYNC TASK ───────────────────────────────────────────────────────

@shared_task
def sync_workspace_to_disk(workspace_id):
    """
    Workspace fayllarini DB dan diskka sinxronlash (background).
    Server restart'dan keyin chaqiriladi.
    """
    from apps.workspace.models import Workspace
    import os
    from pathlib import Path

    try:
        workspace = Workspace.objects.get(pk=workspace_id)
        base_dir = Path(settings.BASE_DIR) / 'workspaces' / str(workspace_id)
        base_dir.mkdir(parents=True, exist_ok=True)

        synced = 0
        for f in workspace.files.filter(is_folder=False):
            rel_path = f.path.strip('/')
            file_dir = base_dir / rel_path if rel_path else base_dir
            file_dir.mkdir(parents=True, exist_ok=True)
            file_path = file_dir / f.name
            try:
                with open(file_path, 'w', encoding='utf-8') as fs:
                    fs.write(f.content or '')
                synced += 1
            except Exception as e:
                logger.warning(f"Could not sync file {f.name}: {e}")

        logger.info(f"Workspace #{workspace_id} synced {synced} files to disk")
        return {"workspace": workspace_id, "synced": synced}
    except Exception as e:
        logger.error(f"sync_workspace_to_disk error (workspace={workspace_id}): {e}")
        return {"error": str(e)}


@shared_task
def sync_all_workspaces():
    """Barcha workspace'larni diskka sinxronlash (startup task)"""
    from apps.workspace.models import Workspace
    ids = list(Workspace.objects.values_list('pk', flat=True))
    for wid in ids:
        sync_workspace_to_disk.delay(wid)
    return {"queued": len(ids)}


# ── AI USAGE ANALYTICS TASK ───────────────────────────────────────────────────

@shared_task
def cleanup_expired_rate_limits():
    """Cache-dan eskirgan rate-limit yozuvlarini tozalash"""
    from django.core.cache import cache
    # django-ratelimit o'z-o'zidan boshqaradi, lekin
    # custom usage tracking uchun saqlab qolildi
    logger.info("Rate limit cleanup completed")
# ── LEADERBOARD & CHALLENGE TASKS ──────────────────────────────────────────────

@shared_task
def update_weekly_leaderboard():
    """
    Har hafta boshida (yoki dushanba 00:00) yangi haftalik reyting jadvalini yaratadi.
    """
    from apps.accounts.models import User, WeeklyLeaderboard, UserActivity
    from datetime import date, timedelta
    from django.db.models import Count
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    # Oxirgi haftadagi XP yig'indisini hisoblash (UserActivity orqali taxminiy yoki 
    # to'g'ridan-to'g'ri user XP o'zgarishini kuzatish kerak bo'ladi).
    # Hozircha oddiyroq usul: Haftalik faollik soni bo'yicha.
    
    activities = UserActivity.objects.filter(
        created_at__date__gte=week_start
    ).values('user').annotate(total=Count('id')).order_by('-total')
    
    for rank, item in enumerate(activities, 1):
        user_id = item['user']
        xp_gained = item['total'] * 10 # Har bir faollik uchun 10 XP
        
        WeeklyLeaderboard.objects.update_or_create(
            user_id=user_id,
            week_start=week_start,
            defaults={'xp_gained': xp_gained, 'rank': rank}
        )
    
    logger.info(f"Weekly leaderboard updated for {week_start}")
    return {"status": "success", "week": str(week_start), "entries": len(activities)}


@shared_task
def process_challenge_action(user_id, action_type):
    """
    Foydalanuvchi biror amal bajarganda challenge progressini yangilash.
    """
    from apps.challenges.models import ChallengeParticipant
    from django.utils import timezone
    
    now = timezone.now()
    participants = ChallengeParticipant.objects.filter(
        user_id=user_id,
        completed=False,
        challenge__action_type=action_type,
        challenge__is_active=True,
        challenge__start_date__lte=now,
        challenge__end_date__gte=now
    )
    
    updated_count = 0
    for p in participants:
        p.increment()
        updated_count += 1
        
    return {"user_id": user_id, "action": action_type, "updated_challenges": updated_count}
