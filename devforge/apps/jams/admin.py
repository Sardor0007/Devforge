# apps/jams/admin.py
from django.contrib import admin
from .models import Jam, JamSubmission

@admin.register(Jam)
class JamAdmin(admin.ModelAdmin):
    list_display = ('title', 'theme', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date')
    search_fields = ('title', 'theme')

@admin.register(JamSubmission)
class JamSubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'jam', 'creator', 'votes', 'created_at')
    list_filter = ('jam', 'creator')
    search_fields = ('title', 'jam__title', 'creator__username')
