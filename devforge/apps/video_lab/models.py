from django.db import models
from apps.accounts.models import User

class VideoProject(models.Model):
    """Video editing project with timeline data, transitions, subtitles, etc."""
    title = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_projects')
    video_file = models.FileField(upload_to='video_lab/files/', blank=True, null=True)
    timeline = models.JSONField(default=dict, blank=True, help_text='Serialized timeline data')
    subtitles = models.TextField(blank=True)
    video_filter = models.CharField(max_length=500, blank=True, default='none')  # CSS filter string
    media_items = models.JSONField(default=list, blank=True)  # Saved media pool items
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

