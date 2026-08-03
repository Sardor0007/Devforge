# apps/jams/models.py
from django.db import models
from django.utils import timezone
from apps.accounts.models import User

class Jam(models.Model):
    """Game Jam event definition"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    theme = models.CharField(max_length=100, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_jams')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Game Jam'
        verbose_name_plural = 'Game Jams'

    def __str__(self):
        return self.title

    @property
    def is_running(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

class JamSubmission(models.Model):
    """Submission for a particular jam"""
    jam = models.ForeignKey(Jam, on_delete=models.CASCADE, related_name='submissions')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jam_submissions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='jams/submissions/')
    demo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    votes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-votes', '-created_at']
        unique_together = [('jam', 'creator')]
        verbose_name = 'Jam Submission'
        verbose_name_plural = 'Jam Submissions'

    def __str__(self):
        return f"{self.title} ({self.jam.title})"
