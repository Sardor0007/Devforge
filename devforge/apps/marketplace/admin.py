from django.contrib import admin
from .models import Service, Order, Review

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'category', 'price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    list_editable = ['is_active']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'status', 'amount', 'created_at']
    list_filter = ['status']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['service', 'reviewer', 'rating', 'created_at']
