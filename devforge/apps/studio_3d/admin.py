from django.contrib import admin
from .models import Asset3D, Scene3D, AssetCategory


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "icon"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Asset3D)
class Asset3DAdmin(admin.ModelAdmin):
    list_display = ["title", "creator", "format", "file_size_mb", "is_public", "created_at"]
    list_filter  = ["format", "is_public", "category"]
    search_fields = ["title", "creator__username"]
    readonly_fields = ["file_size", "download_count", "created_at", "updated_at"]


@admin.register(Scene3D)
class Scene3DAdmin(admin.ModelAdmin):
    list_display = ["title", "creator", "template", "object_count", "is_public", "updated_at"]
    list_filter  = ["template", "is_public"]
    search_fields = ["title", "creator__username"]
    readonly_fields = ["created_at", "updated_at"]