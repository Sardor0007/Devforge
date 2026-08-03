# apps/image_editor/admin.py
from django.contrib import admin
from .models import ImageProject, ImageLayer, TextLayer


@admin.register(ImageProject)
class ImageProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'width', 'height', 'get_layer_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'owner')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Project Info', {
            'fields': ('title', 'description', 'owner')
        }),
        ('Dimensions', {
            'fields': ('width', 'height')
        }),
        ('Files', {
            'fields': ('base_image', 'thumbnail', 'canvas_data')
        }),
        ('Layers', {
            'fields': ('layers', 'layer_order'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_layer_count(self, obj):
        return obj.get_layer_count()
    get_layer_count.short_description = 'Layers'


@admin.register(ImageLayer)
class ImageLayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'layer_type', 'visible', 'locked', 'opacity', 'order')
    list_filter = ('layer_type', 'visible', 'locked', 'project')
    search_fields = ('name', 'project__title')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Layer Info', {
            'fields': ('project', 'name', 'layer_type')
        }),
        ('Appearance', {
            'fields': ('opacity', 'blend_mode', 'visible', 'locked')
        }),
        ('Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Order', {
            'fields': ('order',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TextLayer)
class TextLayerAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'layer', 'font_family', 'font_size', 'color')
    list_filter = ('font_family', 'font_size')
    search_fields = ('text', 'layer__name')
    readonly_fields = ('layer',)
    
    fieldsets = (
        ('Layer Reference', {
            'fields': ('layer',)
        }),
        ('Text Content', {
            'fields': ('text',)
        }),
        ('Font Settings', {
            'fields': ('font_family', 'font_size', 'font_weight', 'color')
        }),
        ('Position', {
            'fields': ('x', 'y')
        }),
    )
    
    def text_preview(self, obj):
        preview = obj.text[:50] + ('...' if len(obj.text) > 50 else '')
        return preview
    text_preview.short_description = 'Text'
