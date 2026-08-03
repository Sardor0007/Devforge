"""
DevForge — Bildirishnomalar Yaratish Yordamchi Moduli
Hamma joydan import qilib ishlatiladi:
    from apps.notifications.service import notify
"""
from .models import Notification


def notify(recipient, notif_type, title, message='', link='', sender=None):
    """
    Bildirishnoma yaratish — asosiy funksiya.
    recipient: User obyekti
    sender:    User | None
    """
    if recipient == sender:
        return None  # O'ziga bildirishnoma yubormaydi
    notif = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notif_type=notif_type,
        title=title,
        message=message,
        link=link,
    )

    # Real-time Broadcast via WebSocket
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notify_{recipient.id}",
            {
                "type": "send_notification",
                "data": {
                    "id": notif.id,
                    "title": notif.title,
                    "message": notif.message,
                    "link": notif.link,
                    "type": notif.notif_type,
                    "sender": sender.username if sender else 'System',
                    "time": "Hozirgina"
                }
            }
        )
    except Exception as e:
        print(f"WebSocket notification error: {e}")

    # Email Bildirishnoma (asinxron thread)
    try:
        from .email_service import send_notification_email_async
        if recipient.email:
            send_notification_email_async(
                recipient_email=recipient.email,
                title=title,
                message=message,
                link=link
            )
    except Exception as e:
        print(f"Email notification dispatch error: {e}")

    return notif


# ── LOYIHA BILDIRISHNOMALARI ──────────────────────────────────────────────────

def notify_project_apply(project, applicant):
    """Loyiha egasiga: kimdir ariza berdi"""
    notify(
        recipient=project.creator,
        sender=applicant,
        notif_type='project_apply',
        title=f"{applicant.username} loyihangizga ariza berdi",
        message=f'"{project.title}" loyihasiga qo\'shilish uchun ariza yuborildi.',
        link=f'/dashboard/projects/{project.pk}/',
    )


def notify_project_approved(member, project):
    """Ariza berganga: qabul qilindi"""
    notify(
        recipient=member,
        sender=project.creator,
        notif_type='project_approved',
        title=f"Arizangiz qabul qilindi! 🎉",
        message=f'Siz "{project.title}" loyihasiga a\'zo bo\'ldingiz.',
        link=f'/dashboard/projects/{project.pk}/',
    )


def notify_project_rejected(member, project):
    """Ariza berganga: rad etildi"""
    notify(
        recipient=member,
        sender=project.creator,
        notif_type='project_rejected',
        title=f"Arizangiz rad etildi",
        message=f'"{project.title}" loyihasiga arizangiz qabul qilinmadi.',
        link=f'/dashboard/projects/',
    )


def notify_new_member(project, new_member):
    """Jamoa a'zolariga: yangi a'zo qo'shildi"""
    existing = project.members.filter(is_approved=True).exclude(user=new_member)
    for m in existing:
        notify(
            recipient=m.user,
            sender=new_member,
            notif_type='project_member',
            title=f"{new_member.username} jamoaga qo'shildi",
            message=f'"{project.title}" loyihasiga yangi a\'zo qo\'shildi.',
            link=f'/dashboard/projects/{project.pk}/',
        )


# ── VAZIFA BILDIRISHNOMALARI ──────────────────────────────────────────────────

def notify_task_assigned(task, assigned_by):
    """Foydalanuvchiga: vazifa belgilandi"""
    if not task.assigned_to:
        return
    notify(
        recipient=task.assigned_to,
        sender=assigned_by,
        notif_type='task_assigned',
        title=f"Sizga vazifa belgilandi: {task.title}",
        message=f'"{task.project.title}" loyihasida yangi vazifa.',
        link=f'/dashboard/projects/{task.project.pk}/',
    )


def notify_task_completed(task, completed_by):
    """Loyiha egasiga: vazifa bajarildi"""
    notify(
        recipient=task.project.creator,
        sender=completed_by,
        notif_type='task_completed',
        title=f"Vazifa bajarildi: {task.title}",
        message=f'"{task.project.title}" loyihasidagi vazifa yakunlandi.',
        link=f'/dashboard/projects/{task.project.pk}/',
    )


# ── AKTIV BILDIRISHNOMALARI ───────────────────────────────────────────────────

def notify_asset_liked(asset, liker):
    """Aktiv egasiga: like bosildi"""
    notify(
        recipient=asset.creator,
        sender=liker,
        notif_type='asset_liked',
        title=f"{liker.username} aktivingizni yoqtirdi ❤️",
        message=f'"{asset.title}" aktivingizga like qo\'yildi.',
        link=f'/assets/{asset.pk}/',
    )


def notify_asset_downloaded(asset, downloader):
    """Aktiv egasiga: yuklab olindi"""
    notify(
        recipient=asset.creator,
        sender=downloader,
        notif_type='asset_downloaded',
        title=f"{downloader.username} aktivingizni yuklab oldi",
        message=f'"{asset.title}" aktivingiz yuklab olindi.',
        link=f'/assets/{asset.pk}/',
    )


# ── MARKETPLACE BILDIRISHNOMALARI ─────────────────────────────────────────────

def notify_order_placed(order):
    """Sotuvchiga: yangi buyurtma keldi"""
    notify(
        recipient=order.service.seller,
        sender=order.buyer,
        notif_type='order_placed',
        title=f"Yangi buyurtma! 🛒",
        message=f'{order.buyer.username} "{order.service.title}" xizmatingizga buyurtma berdi. Summa: ${order.amount}',
        link=f'/marketplace/orders/',
    )


def notify_order_completed(order):
    """Buyurtmachiga: buyurtma bajarildi"""
    notify(
        recipient=order.buyer,
        sender=order.service.seller,
        notif_type='order_completed',
        title=f"Buyurtmangiz bajarildi! ✅",
        message=f'"{order.service.title}" xizmati yetkazib berildi.',
        link=f'/marketplace/orders/',
    )


def notify_review_received(review):
    """Sotuvchiga: yangi sharh"""
    notify(
        recipient=review.service.seller,
        sender=review.reviewer,
        notif_type='review_received',
        title=f"{review.reviewer.username} sharh qoldirdi: {review.rating}★",
        message=f'"{review.service.title}" xizmatingizga yangi sharh: {review.comment[:80]}',
        link=f'/marketplace/{review.service.pk}/',
    )


# ── ISH O'RINLARI BILDIRISHNOMALARI (JOBS) ───────────────────────────────────

def notify_proposal_accepted(proposal):
    """Workerga: arizasi qabul qilindi"""
    notify(
        recipient=proposal.worker,
        sender=proposal.job.client,
        notif_type='proposal_accepted',
        title=f"Arizangiz qabul qilindi! 🎉",
        message=f'"{proposal.job.title}" ishi uchun siz tanlandingiz. Mijoz to\'lov qilishini kuting.',
        link=f'/jobs/{proposal.job.pk}/',
    )


def notify_escrow_funded(job):
    """Workerga: mijoz to'lov qildi, ishni boshlash mumkin"""
    notify(
        recipient=job.selected_worker,
        sender=job.client,
        notif_type='escrow_funded',
        title=f"To'lov amalga oshirildi! 💰",
        message=f'"{job.title}" ishi uchun mablag\' escrow\'ga qo\'yildi. Ishni boshlashingiz mumkin.',
        link=f'/jobs/{job.pk}/',
    )


def notify_delivery_submitted(job):
    """Mijozga: ish topshirildi"""
    notify(
        recipient=job.client,
        sender=job.selected_worker,
        notif_type='delivery_submitted',
        title=f"Ish topshirildi 📩",
        message=f'"{job.title}" ishi bo\'yicha natija yuborildi. Ko\'rib chiqing va tasdiqlang.',
        link=f'/jobs/{job.pk}/',
    )


def notify_delivery_approved(job):
    """Workerga: ish tasdiqlandi va pul chiqarildi"""
    notify(
        recipient=job.selected_worker,
        sender=job.client,
        notif_type='delivery_approved',
        title=f"Ish tasdiqlandi! ✅",
        message=f'"{job.title}" ishi mijoz tomonidan qabul qilindi. Pul balansingizga o\'tkazildi.',
        link=f'/jobs/{job.pk}/',
    )


# ── TIZIM BILDIRISHNOMALARI ───────────────────────────────────────────────────

def notify_system(recipient, title, message='', link=''):
    """Tizim xabari"""
    notify(
        recipient=recipient,
        notif_type='system',
        title=title,
        message=message,
        link=link,
    )
