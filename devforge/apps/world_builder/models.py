from django.db import models
from apps.accounts.models import User

class WorldMap(models.Model):
    """World Builder map planning (dungeons, villages, castle layouts, etc.)"""
    MAP_TYPE_CHOICES = [
        ('dungeon', 'Dungeon Planning'),
        ('village', 'Village Planning'),
        ('castle', 'Castle Layout'),
        ('level', 'Level Design'),
        ('architecture', 'Architecture Sketch'),
    ]
    title = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='world_maps')
    map_type = models.CharField(max_length=50, choices=MAP_TYPE_CHOICES, default='level')
    data = models.JSONField(default=dict, blank=True, help_text='Serialized map grid/sketch data')
    thumbnail = models.ImageField(upload_to='world_builder/thumbs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_map_type_display()})"
