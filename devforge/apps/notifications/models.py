from django.db import models
from apps.accounts.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        # Loyiha
        ('project_apply',    '📨 Loyihaga ariza'),
        ('project_approved', '✅ Arizangiz qabul qilindi'),
        ('project_rejected', '❌ Arizangiz rad etildi'),
        ('project_member',   '👥 Yangi a\'zo qo\'shildi'),
        ('project_created',  '🚀 Yangi loyiha'),
        # Vazifa
        ('task_assigned',    '📋 Vazifa belgilandi'),
        ('task_completed',   '✓ Vazifa bajarildi'),
        # Aktivlar
        ('asset_liked',      '❤️ Aktivingizga like'),
        ('asset_downloaded', '⬇️ Aktivingiz yuklandi'),
        # Marketplace
        ('order_placed',     '🛒 Yangi buyurtma'),
        ('order_completed',  '✅ Buyurtma bajarildi'),
        ('review_received',  '⭐ Yangi sharh'),
        # Tizim
        ('system',           '🔔 Tizim xabari'),
        ('mention',          '@ Eslatilish'),
    ]

    recipient  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notif_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='system')
    title      = models.CharField(max_length=200)
    message    = models.TextField(blank=True)
    link       = models.CharField(max_length=500, blank=True)  # relative URL
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"→ {self.recipient.username}: {self.title}"

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    @property
    def icon(self):
        icons = {
            'project_apply':    '📨',
            'project_approved': '✅',
            'project_rejected': '❌',
            'project_member':   '👥',
            'project_created':  '🚀',
            'task_assigned':    '📋',
            'task_completed':   '✓',
            'asset_liked':      '❤️',
            'asset_downloaded': '⬇️',
            'order_placed':     '🛒',
            'order_completed':  '✅',
            'review_received':  '⭐',
            'system':           '🔔',
            'mention':          '@',
        }
        return icons.get(self.notif_type, '🔔')
