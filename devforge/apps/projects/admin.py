from django.contrib import admin
from .models import Project, ProjectRole, ProjectMember, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'genre', 'status', 'visibility', 'created_at']
    list_filter = ['genre', 'status', 'visibility']
    search_fields = ['title', 'description']


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'is_approved', 'joined_at']
    list_filter = ['is_approved']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'assigned_to', 'status', 'priority']
    list_filter = ['status', 'priority']
