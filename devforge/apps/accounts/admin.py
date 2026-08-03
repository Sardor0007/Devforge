from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Skill, PortfolioItem, UserActivity,
    Transaction, UserBalance, Subscription,
    Badge, UserBadge, SocialProfile,
    WeeklyLeaderboard, FreelancerReview,
    AdminWalletAuditLog,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'email', 'role', 'subscription_type', 'balance', 'is_verified', 'stripe_customer_id', 'created_at']
    list_filter   = ['role', 'subscription_type', 'is_verified', 'is_staff']
    search_fields = ['username', 'email', 'stripe_customer_id']
    fieldsets     = UserAdmin.fieldsets + (
        ('DevForge', {'fields': (
            'role', 'subscription_type', 'balance', 'stripe_customer_id',
            'avatar', 'bio', 'location', 'website', 'github',
            'is_verified', 'onboarding_completed', 'xp', 'level',
        )}),
    )


@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display    = ['user', 'deposit_balance', 'earnings_balance', 'total_balance', 'updated_at']
    search_fields   = ['user__username', 'user__email']
    readonly_fields = ['deposit_balance', 'earnings_balance', 'updated_at']

    def total_balance(self, obj):
        return obj.total_balance
    total_balance.short_description = 'Jami'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Admin Django admin panelida balansni to'g'ridan to'g'ri o'zgartira olmaydi
        return False


@admin.register(AdminWalletAuditLog)
class AdminWalletAuditLogAdmin(admin.ModelAdmin):
    list_display    = ['created_at', 'admin', 'target_user', 'wallet_type', 'action_type', 'amount', 'balance_before', 'balance_after']
    list_filter     = ['wallet_type', 'action_type', 'created_at']
    search_fields   = ['admin__username', 'target_user__username', 'reason']
    readonly_fields = ['admin', 'target_user', 'wallet_type', 'action_type',
                       'amount', 'balance_before', 'balance_after', 'reason',
                       'ip_address', 'created_at']

    def has_add_permission(self, request):
        return False  # Faqat tizim yozadi

    def has_change_permission(self, request, obj=None):
        return False  # O'zgartirib bo'lmaydi

    def has_delete_permission(self, request, obj=None):
        return False  # O'chirib bo'lmaydi


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display  = ['user', 'plan', 'status', 'expires_at', 'stripe_subscription_id', 'updated_at']
    list_filter   = ['plan', 'status']
    search_fields = ['user__username', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['cancel_subscriptions']

    def cancel_subscriptions(self, request, queryset):
        for sub in queryset:
            sub.cancel()
        self.message_user(request, f"{queryset.count()} ta obuna bekor qilindi.")
    cancel_subscriptions.short_description = "Tanlangan obunalarni bekor qilish"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display  = ['user', 'transaction_type', 'wallet_type', 'amount', 'description', 'created_at']
    list_filter   = ['transaction_type', 'wallet_type']
    search_fields = ['user__username', 'description', 'stripe_payment_intent']
    readonly_fields = ['created_at']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'created_at']
    list_filter  = ['activity_type']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'level']
    list_filter  = ['level']


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'item_type', 'created_at']


@admin.register(SocialProfile)
class SocialProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'provider', 'github_username', 'created_at']
    search_fields = ['user__username', 'github_username']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'xp_reward', 'created_at']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display  = ['user', 'badge', 'earned_at']
    list_filter   = ['badge']


@admin.register(WeeklyLeaderboard)
class WeeklyLeaderboardAdmin(admin.ModelAdmin):
    list_display = ['rank', 'user', 'xp_gained', 'week_start']
    list_filter  = ['week_start']


@admin.register(FreelancerReview)
class FreelancerReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'worker', 'rating', 'created_at']
    list_filter  = ['rating']
