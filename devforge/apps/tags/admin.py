from django.contrib import admin
from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'usage_count', 'created_at']
    search_fields = ['name', 'slug']
    list_filter = ['created_at']
    readonly_fields = ['slug', 'usage_count', 'created_at']
    ordering = ['-usage_count']
