from django.contrib import admin
from .models import Job, Proposal, EscrowPayment, Delivery, Dispute

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'selected_worker', 'budget', 'status', 'created_at']
    list_filter = ['status', 'visibility']
    search_fields = ['title', 'description']

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ['worker', 'job', 'price', 'status', 'created_at']
    list_filter = ['status']

@admin.register(EscrowPayment)
class EscrowPaymentAdmin(admin.ModelAdmin):
    list_display = ['job', 'amount', 'status', 'created_at']
    list_filter = ['status']

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['job', 'worker', 'status', 'is_downloadable', 'created_at']
    list_filter = ['status']

@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ['job', 'opened_by', 'status', 'created_at']
    list_filter = ['status']
