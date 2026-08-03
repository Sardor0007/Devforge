from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    """
    Universal tag tizimi — Post, Asset, Project, Job, Course uchun
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    color = models.CharField(max_length=7, default='#6366f1', help_text="Hex rang kodi")
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-usage_count', 'name']
        indexes = [
            models.Index(fields=['-usage_count']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def increment_usage(self):
        Tag.objects.filter(pk=self.pk).update(usage_count=models.F('usage_count') + 1)

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create_tag(cls, name: str):
        """Tag nomidan slug yaratib, tag topadi yoki yaratadi"""
        slug = slugify(name.strip())
        tag, created = cls.objects.get_or_create(
            slug=slug,
            defaults={'name': name.strip()[:50]}
        )
        if not created:
            tag.increment_usage()
        return tag

    @classmethod
    def popular(cls, limit=20):
        return cls.objects.order_by('-usage_count')[:limit]
