from django.db import models
from django.conf import settings

class StudioProject(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='studio_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    settings_data = models.JSONField(default=dict)

    def __str__(self):
        return self.title

class StudioObject(models.Model):
    OBJECT_TYPES = [
        ('mesh', 'Uploaded Mesh'),
        ('primitive', 'Primitive Shape'),
        ('light', 'Light Source'),
    ]
    project = models.ForeignKey(StudioProject, on_delete=models.CASCADE, related_name='scene_objects')
    name = models.CharField(max_length=255)
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    transform_data = models.JSONField(default=dict)
    properties_data = models.JSONField(default=dict)
    asset_file = models.FileField(upload_to='studio/assets/', blank=True, null=True)
    original_filename = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
