from django.db import models
from apps.accounts.models import User

class Conversation(models.Model):
    """Ikki foydalanuvchi o'rtasidagi suhbat"""
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        names = ', '.join(p.username for p in self.participants.all())
        return f"Suhbat: {names}"

    def other_participant(self, user):
        return self.participants.exclude(pk=user.pk).first()

    def last_message(self):
        return self.messages.order_by('-created_at').first()

    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    @classmethod
    def get_or_create_between(cls, user1, user2):
        """Ikki foydalanuvchi o'rtasida suhbat topish yoki yaratish"""
        conv = cls.objects.filter(
            participants=user1
        ).filter(
            participants=user2
        ).first()
        if not conv:
            conv = cls.objects.create()
            conv.participants.add(user1, user2)
        return conv


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content      = models.TextField(blank=True)
    attachment   = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    is_read      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:40] or 'Fayl'}"

    @property
    def is_image(self):
        if not self.attachment: return False
        ext = self.attachment.name.lower().split('.')[-1]
        return ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']

    @property
    def is_video(self):
        if not self.attachment: return False
        ext = self.attachment.name.lower().split('.')[-1]
        return ext in ['mp4', 'webm', 'ogg', 'mov']
