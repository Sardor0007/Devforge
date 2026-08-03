from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('developer', 'O\'yin Dasturchisi'),
        ('artist', '3D Rassom'),
        ('programmer', 'Dasturchi'),
        ('designer', 'UI/UX Dizayner'),
        ('studio', 'Studio'),
        ('freelancer', 'Freelancer'),
    ]
    SUBSCRIPTION_CHOICES = [
        ('free',       'Free'),
        ('pro',        'Pro'),
        ('studio',     'Studio'),
        ('enterprise', 'Enterprise'),
        # Eski nomlar (backward compat)
        ('gold',       'Pro'),
        ('platinum',   'Studio'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='developer')
    # balance USD da saqlanadi
    balance = models.DecimalField(max_digits=20, decimal_places=4, default=0.0000)
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='free')
    # Stripe Customer ID
    stripe_customer_id = models.CharField(max_length=60, blank=True, db_index=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    github = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    onboarding_completed = models.BooleanField(default=False)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        indexes = [
            models.Index(fields=['-xp']),            # Leaderboard uchun
            models.Index(fields=['-created_at']),    # Yangi foydalanuvchilar
            models.Index(fields=['subscription_type']),
            models.Index(fields=['role']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def project_count(self):
        return self.created_projects.count()

    @property
    def asset_count(self):
        return self.assets.count()

    @property
    def level_progress(self):
        """Next level XP target: (level * 100) * 1.5"""
        next_level_xp = (self.level * 100) * 1.5
        progress = (self.xp / next_level_xp) * 100
        return min(round(progress), 100)

    def can_use_pro_features(self):
        """Pro, Studio, Enterprise va eski Gold/Platinum obunalar"""
        return self.subscription_type in ['pro', 'studio', 'enterprise', 'gold', 'platinum']

    def can_create_content(self):
        """Kontent yaratish uchun ruxsat — Pro va undan yuqori"""
        return self.subscription_type in ['pro', 'studio', 'enterprise', 'gold', 'platinum']

    def get_upload_limit(self):
        """Oylik yuklash limiti (fayl soni)"""
        limits = {
            'pro':        10,
            'gold':       10,
            'studio':     50,
            'platinum':   50,
            'enterprise': 999,
        }
        return limits.get(self.subscription_type, 0)

    def get_active_subscription(self):
        """Faol Subscription obyektini qaytaradi"""
        try:
            sub = self.subscription
            if sub.is_active:
                return sub
        except Subscription.DoesNotExist:
            pass
        return None

    def add_xp(self, amount):
        self.xp += amount          # <-- o'qiladi
        next_level_xp = (self.level * 100) * 1.5
        while self.xp >= next_level_xp:
            self.level += 1
            next_level_xp = (self.level * 100) * 1.5
        self.save()                # <-- yoziladi


class Skill(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Boshlang\'ich'),
        ('intermediate', 'O\'rta'),
        ('advanced', 'Ilg\'or'),
        ('expert', 'Ekspert'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=50)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='intermediate')

    class Meta:
        indexes = [
            models.Index(fields=['user', 'name']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class PortfolioItem(models.Model):
    TYPE_CHOICES = [
        ('image', 'Rasm'),
        ('video', 'Video'),
        ('link', 'Havola'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='image')
    file = models.FileField(upload_to='portfolio/', blank=True, null=True)
    url = models.URLField(blank=True)
    thumbnail = models.ImageField(upload_to='portfolio/thumbs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class SocialProfile(models.Model):
    """Google/GitHub orqali kirganlar uchun qo'shimcha ma'lumotlar"""
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='social_profile')
    avatar_url  = models.URLField(blank=True)
    provider    = models.CharField(max_length=20, blank=True)
    github_url  = models.URLField(blank=True)
    github_username = models.CharField(max_length=100, blank=True)
    github_repos    = models.JSONField(default=list, blank=True)   # ← GitHub repos cache
    repos_synced_at = models.DateTimeField(null=True, blank=True)   # ← Oxirgi sync vaqti
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} social profile"


class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/')
    xp_reward = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('project', 'Loyiha yaratdi'),
        ('asset', 'Aktiv yukladi'),
        ('post', 'Feedga post qo\'shdi'),
        ('comment', 'Izoh qoldirdi'),
        ('task', 'Vazifa bajardi'),
        ('course_complete', 'Kursni tugatdi'),
        ('job_complete', 'Ishni yakunladi'),
        ('challenge', 'Challenge bajardi'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),   # Heatmap query
            models.Index(fields=['activity_type']),
        ]

    @classmethod
    def log_activity(cls, user, activity_type):
        """Activity log yaratish va XP qo'shish"""
        activity = cls.objects.create(user=user, activity_type=activity_type)
        
        # XP miqdori activity turiga qarab
        xp_rewards = {
            'project': 100,
            'asset': 150,
            'post': 20,
            'comment': 10,
            'task': 50,
            'course_complete': 300,
            'job_complete': 500,
            'challenge': 200,
        }
        reward = xp_rewards.get(activity_type, 10)
        user.add_xp(reward)

        # Challenge progress update logic
        try:
            from django.utils import timezone
            from apps.challenges.models import ChallengeParticipant
            now = timezone.now()
            participants = ChallengeParticipant.objects.filter(
                user=user,
                completed=False,
                challenge__is_active=True,
                challenge__action_type=activity_type,
                challenge__start_date__lte=now,
                challenge__end_date__gte=now
            )
            for p in participants:
                p.increment()
                # If challenge was just completed, record a challenge completion activity
                if p.completed:
                    cls.objects.create(user=user, activity_type='challenge')
        except Exception as e:
            print(f"Error updating challenge progress: {e}")

        return activity

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} ({self.created_at.date()})"


class Transaction(models.Model):
    """Barcha moliyaviy harakatlar USD da saqlanadi"""
    TRANSACTION_TYPES = [
        ('deposit',        'Depazit to\'ldirish'),
        ('withdrawal',     'Pul yechish (foyda)'),
        ('purchase',       'Sotib olish'),
        ('sale',           'Sotish (Daromad)'),
        ('escrow_lock',    'Escrowda muzlatish'),
        ('escrow_release', 'Escrowdan chiqarish'),
        ('escrow_refund',  'Escrowdan qaytarish'),
        ('subscription',   'Obuna uchun to\'lov'),
        ('prize',          'Tournament mukofoti'),
        ('refund',         'Qaytarish'),
        ('transfer_to_deposit', 'Foydadan Depazitga o\'tkazma'),
        ('admin_adjustment',    'Admin tomonidan tuzatish'),
    ]
    WALLET_TYPES = [
        ('deposit',  'Depazit hamyon'),
        ('earnings', 'Foyda hamyon'),
        ('both',     'Ikkalasi'),
    ]
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount           = models.DecimalField(max_digits=20, decimal_places=4)   # USD
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    wallet_type      = models.CharField(max_length=10, choices=WALLET_TYPES, default='deposit')
    description      = models.CharField(max_length=500, blank=True)
    stripe_payment_intent = models.CharField(max_length=100, blank=True)      # pi_xxx
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['wallet_type']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.transaction_type} (${self.amount}) [{self.wallet_type}]"


# ── USER BALANCE (Dual Wallet) ────────────────────────────────────────────────

class UserBalance(models.Model):
    """
    Ikki hamyon tizimi:
      deposit_balance  — foydalanuvchi to'ldirgan pul (Stripe orqali)
                         obuna va xaridlar uchun ishlatiladi
      earnings_balance — sotish / vazifa / mukofot daromadlari
                         faqat yechib olish yoki depazitga o'tkazish mumkin

    QOIDALAR:
      ✅ deposit  → xarid, obuna
      ✅ earnings → withdraw (bankga)
      ✅ earnings → deposit  (o'tkazma)
      ❌ deposit  → earnings (TAQIQLANGAN)
      ❌ Admin balansni to'g'ridan-to'g'ri o'zgartira olmaydi — faqat
         AdminWalletAuditLog orqali qayd etilgan tuzatishlar mumkin
    """
    user             = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    deposit_balance  = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    earnings_balance = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Wallet (Dual Balance)'

    def __str__(self):
        return f"{self.user.username}: deposit=${self.deposit_balance} | earnings=${self.earnings_balance}"

    @property
    def total_balance(self):
        return self.deposit_balance + self.earnings_balance

    # ── DEPAZIT HAMYON ────────────────────────────────────────────────────────

    def credit(self, amount, description='', payment_intent=''):
        """Stripe orqali depazit to'ldirish (faqat depazit hamyonga)"""
        from decimal import Decimal
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError("Depazit miqdori musbat bo'lishi kerak")
        self.deposit_balance += amount
        self.save(update_fields=['deposit_balance', 'updated_at'])
        self.user.balance = self.deposit_balance
        self.user.save(update_fields=['balance'])
        Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='deposit',
            wallet_type='deposit',
            description=description or f'Depazit +${amount}',
            stripe_payment_intent=payment_intent,
        )

    def debit(self, amount, tx_type='purchase', description=''):
        """Depazit hamyonidan xarid/obuna uchun yechish"""
        from decimal import Decimal
        amount = Decimal(str(amount))
        if self.deposit_balance < amount:
            raise ValueError(
                f"Depazit hamyonda yetarli mablag\' yo\'q: "
                f"${self.deposit_balance:.2f} < ${amount:.2f}"
            )
        self.deposit_balance -= amount
        self.save(update_fields=['deposit_balance', 'updated_at'])
        self.user.balance = self.deposit_balance
        self.user.save(update_fields=['balance'])
        Transaction.objects.create(
            user=self.user,
            amount=-amount,
            transaction_type=tx_type,
            wallet_type='deposit',
            description=description or f'Depazit -{tx_type} ${amount}',
        )

    # ── FOYDA HAMYON ──────────────────────────────────────────────────────────

    def earn(self, amount, description='', tx_type='sale'):
        """Sotish/vazifa/mukofot daromadini foyda hamyoniga qo'shish"""
        from decimal import Decimal
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError("Daromad miqdori musbat bo'lishi kerak")
        self.earnings_balance += amount
        self.save(update_fields=['earnings_balance', 'updated_at'])
        Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type=tx_type,
            wallet_type='earnings',
            description=description or f'Daromad +${amount}',
        )

    def withdraw(self, amount, description='Pul yechish'):
        """Foyda hamyonidan bankga/kartaga pul yechish so'rovi"""
        from decimal import Decimal
        amount = Decimal(str(amount))
        if self.earnings_balance < amount:
            raise ValueError(
                f"Foyda hamyonda yetarli mablag\' yo\'q: "
                f"${self.earnings_balance:.2f} < ${amount:.2f}"
            )
        self.earnings_balance -= amount
        self.save(update_fields=['earnings_balance', 'updated_at'])
        Transaction.objects.create(
            user=self.user,
            amount=-amount,
            transaction_type='withdrawal',
            wallet_type='earnings',
            description=description,
        )

    def transfer_to_deposit(self, amount, description='Foydadan depazitga o\'tkazma'):
        """Foyda → Depazit (RUXSAT). Depazit → Foyda TAQIQLANGAN."""
        from decimal import Decimal
        amount = Decimal(str(amount))
        if self.earnings_balance < amount:
            raise ValueError(
                f"Foyda hamyonda yetarli mablag\' yo\'q: "
                f"${self.earnings_balance:.2f} < ${amount:.2f}"
            )
        self.earnings_balance -= amount
        self.deposit_balance  += amount
        self.save(update_fields=['deposit_balance', 'earnings_balance', 'updated_at'])
        self.user.balance = self.deposit_balance
        self.user.save(update_fields=['balance'])
        Transaction.objects.create(
            user=self.user,
            amount=-amount,
            transaction_type='transfer_to_deposit',
            wallet_type='earnings',
            description=description,
        )
        Transaction.objects.create(
            user=self.user,
            amount=amount,
            transaction_type='transfer_to_deposit',
            wallet_type='deposit',
            description=description,
        )


# ── ADMIN WALLET AUDIT LOG (O'CHIRIB BO'LMAYDIGAN JURNAL) ────────────────────

class AdminWalletAuditLog(models.Model):
    """
    Admin tomonidan hamyon o'zgarishlarining o'chirib bo'lmaydigan jurnali.
    Hech qanday DELETE yoki UPDATE amalga oshirilmaydi — faqat INSERT.
    """
    WALLET_TYPES = [
        ('deposit',  'Depazit'),
        ('earnings', 'Foyda'),
    ]
    ACTION_TYPES = [
        ('credit',   'Qo\'shish (+)'),
        ('debit',    'Ayirish (-)'),
        ('refund',   'Qaytarish'),
        ('correction', 'Xato tuzatish'),
    ]

    # Kim o'zgartirdi
    admin          = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='wallet_audit_actions',
        verbose_name='Admin'
    )
    # Kim haqida
    target_user    = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='wallet_audit_logs',
        verbose_name='Foydalanuvchi'
    )
    wallet_type    = models.CharField(max_length=10, choices=WALLET_TYPES)
    action_type    = models.CharField(max_length=15, choices=ACTION_TYPES)
    amount         = models.DecimalField(max_digits=20, decimal_places=4)
    balance_before = models.DecimalField(max_digits=20, decimal_places=4)
    balance_after  = models.DecimalField(max_digits=20, decimal_places=4)
    reason         = models.TextField(verbose_name='Sabab (majburiy)')  # admin izohi
    ip_address     = models.GenericIPAddressField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Admin Hamyon Audit Log'
        indexes = [
            models.Index(fields=['target_user', '-created_at']),
            models.Index(fields=['admin', '-created_at']),
        ]

    def __str__(self):
        return (
            f"[{self.created_at:%Y-%m-%d %H:%M}] "
            f"{self.admin.username if self.admin else 'System'} → "
            f"@{self.target_user.username} | "
            f"{self.wallet_type} {self.action_type} ${self.amount}"
        )

    # JURNALGA YOZISH — o'chirish/yangilash taqiqlangan
    def delete(self, *args, **kwargs):
        raise PermissionError("Audit log yozuvlari o'chirib bo'lmaydi.")

    def save(self, *args, **kwargs):
        if self.pk:
            raise PermissionError("Audit log yozuvlari o'zgartirib bo'lmaydi.")
        super().save(*args, **kwargs)



# ── SUBSCRIPTION ─────────────────────────────────────────────────────────────

class Subscription(models.Model):
    """
    Foydalanuvchi obunasi — Stripe Recurring Subscription asosida.
    Diagram: plan · expires_at · stripe_id
    """
    PLAN_CHOICES = [
        ('free',       'Free — $0/oy'),
        ('pro',        'Pro — $9/oy'),
        ('studio',     'Studio — $25/oy'),
        ('enterprise', 'Enterprise — Custom'),
    ]
    STATUS_CHOICES = [
        ('active',    'Faol'),
        ('past_due',  'Muddati o\'tgan (to\'lov kutilmoqda)'),
        ('canceled',  'Bekor qilingan'),
        ('trialing',  'Sinov muddati'),
        ('inactive',  'Faol emas'),
    ]

    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan       = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    # Stripe identifikatorlari
    stripe_subscription_id = models.CharField(max_length=100, blank=True, db_index=True)
    stripe_price_id        = models.CharField(max_length=100, blank=True)
    # Vaqt
    expires_at   = models.DateTimeField(null=True, blank=True)
    canceled_at  = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Subscription'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['plan']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.plan} ({self.status})"

    @property
    def is_active(self):
        if self.status not in ('active', 'trialing'):
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def activate(self, plan, stripe_sub_id='', stripe_price_id='', expires_at=None):
        """Obunani faollashtirish"""
        self.plan = plan
        self.status = 'active'
        self.stripe_subscription_id = stripe_sub_id
        self.stripe_price_id = stripe_price_id
        self.expires_at = expires_at
        self.save()
        # User.subscription_type ni sinxron saqlash
        self.user.subscription_type = plan
        self.user.save(update_fields=['subscription_type'])

    def cancel(self):
        self.status = 'canceled'
        self.canceled_at = timezone.now()
        self.save(update_fields=['status', 'canceled_at'])
        self.user.subscription_type = 'free'
        self.user.save(update_fields=['subscription_type'])


# ── LEADERBOARD ───────────────────────────────────────────────────────────────

class WeeklyLeaderboard(models.Model):
    """Haftalik reyting jadvali — Celery task tomonidan yangilanadi"""
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    week_start = models.DateField()
    xp_gained  = models.IntegerField(default=0)
    rank       = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'week_start']
        ordering = ['rank']
        indexes = [
            models.Index(fields=['week_start', 'rank']),
        ]

    def __str__(self):
        return f"Week {self.week_start} | #{self.rank} {self.user.username} ({self.xp_gained} XP)"


# ── FREELANCER REVIEW ─────────────────────────────────────────────────────────

class FreelancerReview(models.Model):
    """Job yakunlangandan so'ng mijoz ishchiga baho beradi"""
    job       = models.OneToOneField('jobs.Job', on_delete=models.CASCADE, related_name='review')
    reviewer  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    worker    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating    = models.PositiveSmallIntegerField(default=5)   # 1–5
    comment   = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['worker', '-created_at']),
        ]

    def __str__(self):
        return f"Review: {self.reviewer.username} → {self.worker.username} ({self.rating}⭐)"


class SiteConfig(models.Model):
    """Global platform/developer configuration and feature flags"""
    key = models.CharField(max_length=100, unique=True)
    value_bool = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Config"
        verbose_name_plural = "Site Configs"

    def __str__(self):
        return f"{self.key}: {self.value_bool}"

    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        try:
            cfg = cls.objects.get(key=key)
            return cfg.value_bool
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_bool(cls, key: str, value: bool, description: str = ""):
        cfg, _ = cls.objects.get_or_create(key=key)
        cfg.value_bool = value
        if description:
            cfg.description = description
        cfg.save()

