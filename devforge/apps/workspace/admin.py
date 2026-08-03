from django.contrib import admin
from .models import Workspace, WorkspaceFile


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['project', 'created_at']


@admin.register(WorkspaceFile)
class WorkspaceFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'workspace', 'language', 'created_by', 'updated_at']
