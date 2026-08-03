from django.contrib import admin
from .models import Challenge, ChallengeParticipant


class ChallengeParticipantInline(admin.TabularInline):
    model = ChallengeParticipant
    extra = 0
    readonly_fields = ['user', 'current_count', 'completed', 'completed_at', 'joined_at']
    can_delete = False


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display  = ['title', 'challenge_type', 'action_type', 'target_count',
                     'xp_reward', 'start_date', 'end_date', 'participant_count', 'is_active']
    list_filter   = ['challenge_type', 'action_type', 'is_active']
    search_fields = ['title']
    inlines       = [ChallengeParticipantInline]
    date_hierarchy = 'start_date'


@admin.register(ChallengeParticipant)
class ChallengeParticipantAdmin(admin.ModelAdmin):
    list_display  = ['user', 'challenge', 'current_count', 'completed', 'joined_at']
    list_filter   = ['completed', 'challenge']
    search_fields = ['user__username']
