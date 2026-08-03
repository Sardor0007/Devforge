from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class ContentLink(models.Model):
    """Generic linking table between any two objects in the platform.
    link_type defines the semantic purpose of the link.
    """
    LINK_CHOICES = [
        ('feed_editor', 'Feed post ↔ Editor'),
        ('asset_studio', 'Marketplace Asset ↔ Studio'),
        ('video_project', 'Video ↔ Project'),
        ('map_project', 'World Map ↔ Project'),
    ]
    link_type = models.CharField(max_length=20, choices=LINK_CHOICES)

    # Source object
    source_ct = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='source_links')
    source_id = models.PositiveIntegerField()
    source = GenericForeignKey('source_ct', 'source_id')

    # Target object
    target_ct = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='target_links')
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_ct', 'target_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('link_type', 'source_ct', 'source_id', 'target_ct', 'target_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_link_type_display()}: {self.source} → {self.target}"
