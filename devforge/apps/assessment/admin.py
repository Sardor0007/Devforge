from django.contrib import admin
from .models import SkillTest, TestQuestion, SkillCertificate, TestAttempt


class TestQuestionInline(admin.TabularInline):
    model = TestQuestion
    extra = 4
    fields = ['order', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct', 'explanation']


@admin.register(SkillTest)
class SkillTestAdmin(admin.ModelAdmin):
    list_display  = ['skill_name', 'difficulty', 'passing_score', 'time_limit', 'question_count', 'is_active']
    list_filter   = ['difficulty', 'is_active']
    search_fields = ['skill_name']
    inlines       = [TestQuestionInline]


@admin.register(SkillCertificate)
class SkillCertificateAdmin(admin.ModelAdmin):
    list_display  = ['user', 'skill_test', 'score', 'passed', 'issued_at']
    list_filter   = ['passed', 'skill_test']
    search_fields = ['user__username', 'skill_test__skill_name']
    readonly_fields = ['issued_at']
