# apps/image_editor/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import base64
import json

User = get_user_model()

class ImageProject(models.Model):
    """Image editing project with canvas data and layers"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_projects')
    
    # Image storage
    base_image = models.ImageField(upload_to='image_editor/base/', null=True, blank=True)
    canvas_data = models.TextField(blank=True, default='')  # Base64 encoded canvas state
    
    # Layer information
    layers = models.JSONField(default=list, blank=True)  # Array of layer objects
    layer_order = models.JSONField(default=list, blank=True)  # Layer IDs in order
    
    # Project metadata
    width = models.IntegerField(default=800)
    height = models.IntegerField(default=600)
    thumbnail = models.ImageField(upload_to='image_editor/thumbnails/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['owner', '-updated_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_layer_count(self):
        return len(self.layers) if self.layers else 0


class ImageLayer(models.Model):
    """Individual layer in an image project"""
    LAYER_TYPES = [
        ('canvas', 'Canvas Layer'),
        ('text', 'Text Layer'),
        ('shape', 'Shape Layer'),
        ('image', 'Image Layer'),
    ]
    
    project = models.ForeignKey(ImageProject, on_delete=models.CASCADE, related_name='layer_objects')
    name = models.CharField(max_length=100, default='Layer')
    layer_type = models.CharField(max_length=20, choices=LAYER_TYPES, default='canvas')
    
    # Layer data
    data = models.JSONField(default=dict, blank=True)  # Stores layer-specific data
    opacity = models.FloatField(default=1.0)  # 0.0 to 1.0
    blend_mode = models.CharField(
        max_length=20,
        default='normal',
        choices=[
            ('normal', 'Normal'),
            ('multiply', 'Multiply'),
            ('screen', 'Screen'),
            ('overlay', 'Overlay'),
            ('soft-light', 'Soft Light'),
            ('hard-light', 'Hard Light'),
            ('color-dodge', 'Color Dodge'),
            ('color-burn', 'Color Burn'),
            ('darken', 'Darken'),
            ('lighten', 'Lighten'),
        ]
    )
    
    # Visibility and locking
    visible = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)
    
    # Order
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-order']
        unique_together = [['project', 'name']]
    
    def __str__(self):
        return f"{self.project.title} - {self.name}"


class TextLayer(models.Model):
    """Text-specific layer data"""
    layer = models.OneToOneField(ImageLayer, on_delete=models.CASCADE, related_name='text_data')
    
    text = models.TextField()
    font_family = models.CharField(max_length=100, default='Arial')
    font_size = models.IntegerField(default=24)
    font_weight = models.CharField(max_length=20, default='normal')
    color = models.CharField(max_length=7, default='#000000')  # Hex color
    
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Text: {self.text[:50]}"
