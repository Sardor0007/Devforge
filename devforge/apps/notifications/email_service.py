"""
DevForge — Email Bildirishnomalar Servisi
Bildirishnomalarni asinxron (background thread) orqali HTML formatda yuboradi.
"""
import threading
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


def send_notification_email_async(recipient_email, title, message='', link=''):
    """Asinxron email yuborish (request-ni sekinlashtirmaydi)"""
    def _send():
        try:
            if not recipient_email or '@' not in recipient_email:
                return

            site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
            action_url = f"{site_url.rstrip('/')}{link}" if link else site_url

            context = {
                'title': title,
                'message': message,
                'action_url': action_url,
                'site_url': site_url,
                'recipient_email': recipient_email,
            }

            html_content = render_to_string('emails/notification_email.html', context)
            text_content = f"{title}\n\n{message}\n\nTafsilotlar: {action_url}"

            subject = f"[DevForge] {title}"
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@devforge.uz')

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[recipient_email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=True)
            logger.info(f"Email notification sent to {recipient_email}")
        except Exception as e:
            logger.warning(f"Failed to send email notification to {recipient_email}: {e}")

    thread = threading.Thread(target=_send)
    thread.daemon = True
    thread.start()
