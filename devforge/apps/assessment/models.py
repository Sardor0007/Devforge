from django.db import models
from django.conf import settings


class SkillTest(models.Model):
    """Ko'nikma sinovlari — Python, Blender, Unity va h.k."""
    DIFFICULTY_CHOICES = [
        ('easy',   '🟢 Oson'),
        ('medium', '🟡 O\'rta'),
        ('hard',   '🔴 Qiyin'),
    ]
    skill_name    = models.CharField(max_length=50, unique=True)
    description   = models.TextField(blank=True)
    icon          = models.CharField(max_length=10, default='🧠')
    difficulty    = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    passing_score = models.IntegerField(default=70)   # % da
    time_limit    = models.IntegerField(default=30)   # daqiqada
    badge_reward  = models.ForeignKey(
        'accounts.Badge', on_delete=models.SET_NULL, null=True, blank=True
    )
    xp_reward     = models.IntegerField(default=100)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['skill_name']

    def __str__(self):
        return f"{self.icon} {self.skill_name} ({self.difficulty})"

    @property
    def question_count(self):
        return self.questions.count()


class TestQuestion(models.Model):
    """Ko'p tanlovli savol"""
    test    = models.ForeignKey(SkillTest, on_delete=models.CASCADE, related_name='questions')
    text    = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct  = models.CharField(max_length=1, choices=[
        ('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')
    ])
    explanation = models.TextField(blank=True)
    order    = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"[{self.test.skill_name}] {self.text[:60]}"


class SkillCertificate(models.Model):
    """Foydalanuvchi sertifikati — muvaffaqiyatli topshirilgan test"""
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    skill_test = models.ForeignKey(SkillTest, on_delete=models.CASCADE, related_name='certificates')
    score      = models.IntegerField()           # foizda (0–100)
    passed     = models.BooleanField(default=False)
    time_taken = models.IntegerField(default=0)  # soniyada
    issued_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'skill_test']
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['user', 'passed']),
        ]

    def __str__(self):
        status = "✅" if self.passed else "❌"
        return f"{status} {self.user.username} — {self.skill_test.skill_name} ({self.score}%)"


class TestAttempt(models.Model):
    """Test jarayonida foydalanuvchi javoblari"""
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    skill_test = models.ForeignKey(SkillTest, on_delete=models.CASCADE)
    answers    = models.JSONField(default=dict)  # {question_id: 'a/b/c/d'}
    started_at = models.DateTimeField(auto_now_add=True)
    finished   = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} — {self.skill_test.skill_name}"
