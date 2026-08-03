# apps/studio_3d/admin.py
from django.contrib import admin
from .models import AssetCategory, Asset3D

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Asset3D)
class Asset3DAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'format', 'created_at')
    list_filter = ('format', 'created_at')
    search_fields = ('title', 'creator__username')
