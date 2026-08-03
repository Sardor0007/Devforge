from django.contrib import admin
from .models import StudioProject, StudioObject

@admin.register(StudioProject)
class StudioProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'created_at', 'updated_at']
    list_filter = ['owner']
    search_fields = ['title', 'owner__username']

@admin.register(StudioObject)
class StudioObjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'object_type']
    list_filter = ['object_type']
