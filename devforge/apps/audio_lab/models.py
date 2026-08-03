from django.db import models
from apps.accounts.models import User

class AudioProject(models.Model):
    """Multi-track audio project (DAW)"""
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audio_projects')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    bpm = models.IntegerField(default=120)
    master_volume = models.FloatField(default=1.0)
    project_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} (BPM: {self.bpm})"


class AudioTrack(models.Model):
    """Uploaded audio asset"""
    TYPE_CHOICES = [
        ('soundtrack', 'Soundtrack'),
        ('ambient', 'Ambient'),
        ('battle', 'Battle'),
        ('sfx', 'SFX'),
    ]
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audio_tracks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    audio_file = models.FileField(upload_to='audio/')
    track_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='sfx')
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_track_type_display()})"
