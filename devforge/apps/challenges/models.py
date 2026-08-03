from django.db import models
from django.conf import settings


class Challenge(models.Model):
    """Haftalik/oylik challenge — foydalanuvchilarni faol ushlab turish uchun"""
    TYPE_CHOICES = [
        ('weekly',  '🗓️ Haftalik'),
        ('monthly', '📅 Oylik'),
        ('special', '⭐ Maxsus'),
        ('beginner', '🌱 Yangi boshlagan'),
    ]
    ACTION_CHOICES = [
        ('post',        'Post yozish'),
        ('project',     'Loyiha yaratish'),
        ('asset',       'Aktiv yuklash'),
        ('job_complete','Ishni yakunlash'),
        ('course',      'Kurs tugatish'),
        ('comment',     'Izoh qoldirish'),
        ('follow',      'Obunachilar qo\'shish'),
        ('cert',        'Sertifikat olish'),
    ]

    title         = models.CharField(max_length=200)
    description   = models.TextField()
    challenge_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='weekly')
    action_type   = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_count  = models.IntegerField(default=1)  # "5 ta post yoz"
    xp_reward     = models.IntegerField(default=50)
    badge_reward  = models.ForeignKey(
        'accounts.Badge', on_delete=models.SET_NULL, null=True, blank=True
    )
    start_date    = models.DateTimeField()
    end_date      = models.DateTimeField()
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['is_active', '-start_date']),
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        return f"{self.get_challenge_type_display()} | {self.title}"

    @property
    def participant_count(self):
        return self.participants.count()


class ChallengeParticipant(models.Model):
    """Foydalanuvchi challenge'ga qo'shilganda"""
    challenge    = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenges')
    current_count = models.IntegerField(default=0)
    completed    = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    joined_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['challenge', 'user']
        indexes = [
            models.Index(fields=['user', 'completed']),
            models.Index(fields=['challenge', 'completed']),
        ]

    def __str__(self):
        status = "✅" if self.completed else f"{self.current_count}/{self.challenge.target_count}"
        return f"{self.user.username} → {self.challenge.title} [{status}]"

    def increment(self):
        """Har bir action bajarilganda chaqiriladi"""
        from django.utils import timezone
        self.current_count += 1
        if self.current_count >= self.challenge.target_count and not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            # XP va badge berish
            self.user.add_xp(self.challenge.xp_reward)
            if self.challenge.badge_reward:
                from apps.accounts.models import UserBadge
                UserBadge.objects.get_or_create(
                    user=self.user,
                    badge=self.challenge.badge_reward
                )
        self.save()
