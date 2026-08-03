from django.contrib import admin
from .models import Asset, AssetCategory, CartItem, PurchasedAsset

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'format', 'price', 'downloads', 'is_approved', 'created_at']
    list_filter = ['format', 'is_approved', 'category']
    list_editable = ['is_approved']
    search_fields = ['title', 'tags']

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'asset', 'created_at']

@admin.register(PurchasedAsset)
class PurchasedAssetAdmin(admin.ModelAdmin):
    list_display = ['user', 'asset', 'price_paid', 'created_at']
