from django.db import models
from apps.accounts.models import User


class AssetCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='🖼️')

    def __str__(self):
        return self.name


class Asset3D(models.Model):
    FORMAT_CHOICES = [
        ('texture', 'Texture'),
        ('concept', 'Concept Art'),
        ('icon', 'Icon'),
        ('banner', 'Banner'),
        ('model', '3D Model'),
    ]
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='studio_3d_assets')
    category = models.ForeignKey(AssetCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='studio_3d/files/')
    thumbnail = models.ImageField(upload_to='studio_3d/thumbs/', blank=True, null=True)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='model')
    tags = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '3D Asset'
        verbose_name_plural = '3D Assets'

    def __str__(self):
        return self.title


class Scene3D(models.Model):
    """Full 3D Scene for the 3D Studio editor."""
    TEMPLATE_CHOICES = [
        ('empty',    'Bo\'sh sahna'),
        ('showcase', 'Showcase'),
        ('terrain',  'Terrain'),
        ('room',     'Room'),
        ('space',    'Space'),
        ('city',     'City'),
        ('nature',   'Nature'),
        ('abstract', 'Abstract'),
    ]
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scenes_3d')
    title = models.CharField(max_length=200, default='Untitled Scene')
    template = models.CharField(max_length=30, choices=TEMPLATE_CHOICES, default='empty')
    scene_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def get_template_display_custom(self):
        return dict(self.TEMPLATE_CHOICES).get(self.template, self.template)
