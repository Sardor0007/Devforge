from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.projects.models import Project


class Job(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public (Hamma ko\'radi)'),
        ('private', 'Private (Faqat bitta developer)'),
    ]
    STATUS_CHOICES = [
        ('open', 'Ochiq'),
        ('funded', 'Mablag\'langan (Escrow)'),
        ('in_progress', 'Jarayonda'),
        ('submitted', 'Topshirildi'),
        ('approved', 'Tasdiqlandi'),
        ('completed', 'Yakunlandi'),
        ('cancelled', 'Bekor qilindi'),
        ('disputed', 'Nizo'),
    ]

    client          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    title           = models.CharField(max_length=255)
    description     = models.TextField()
    budget          = models.DecimalField(max_digits=10, decimal_places=2)
    visibility      = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    selected_worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hired_jobs')
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    deadline        = models.DateField(null=True, blank=True)
    skills_needed   = models.ManyToManyField('tags.Tag', blank=True, related_name='jobs')
    created_at      = models.DateTimeField(auto_now_add=True)
    project         = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='associated_jobs')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['client', '-created_at']),
            models.Index(fields=['selected_worker']),
            models.Index(fields=['visibility', 'status']),
        ]

    def check_auto_approval(self):
        """3 kundan oshgan topshirilgan ishlarni avtomatik tasdiqlash"""
        if self.status == 'submitted':
            last_delivery = self.deliveries.order_by('-created_at').first()
            if last_delivery and (timezone.now() - last_delivery.created_at).days >= 3:
                self.status = 'approved'
                self.save()
                escrow = self.escrow
                escrow.status = 'released'
                escrow.save()
                self.deliveries.all().update(is_downloadable=True)
                return True
        return False

    def __str__(self):
        return self.title


class Proposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('accepted', 'Qabul qilindi'),
        ('rejected', 'Rad etildi'),
    ]
    job           = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='proposals')
    worker        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals')
    price         = models.DecimalField(max_digits=10, decimal_places=2)
    message       = models.TextField()
    delivery_days = models.PositiveIntegerField()
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['job', 'worker']
        indexes = [
            models.Index(fields=['job', 'status']),
        ]

    def __str__(self):
        return f"{self.worker.username} -> {self.job.title}"


class EscrowPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'To\'lov kutilmoqda'),
        ('funded', 'Mablag\'langan'),
        ('released', 'To\'langan'),
        ('refunded', 'Qaytarilgan'),
    ]
    job                 = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='escrow')
    client              = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escrow_payments')
    worker              = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escrow_receivals', null=True, blank=True)
    amount              = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee        = models.DecimalField(max_digits=10, decimal_places=2)
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_provider_id = models.CharField(max_length=100, blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Escrow: {self.job.title} (${self.amount})"


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Yuborilgan'),
        ('approved', 'Tasdiqlangan'),
        ('revision', 'Tuzatish so\'ralgan'),
        ('disputed', 'Nizo'),
    ]
    job           = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='deliveries')
    worker        = models.ForeignKey(User, on_delete=models.CASCADE)
    message       = models.TextField()
    file          = models.FileField(upload_to='jobs/deliveries/')
    preview_image = models.ImageField(upload_to='jobs/previews/', blank=True, null=True)
    demo_link     = models.URLField(blank=True)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    is_downloadable = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delivery: {self.job.title} by {self.worker.username}"


class Dispute(models.Model):
    STATUS_CHOICES = [
        ('open', 'Ochiq'),
        ('resolved', 'Hal qilindi'),
        ('refunded', 'Qaytarildi'),
        ('released', 'To\'lab berildi'),
    ]
    job            = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='disputes')
    opened_by      = models.ForeignKey(User, on_delete=models.CASCADE)
    reason         = models.TextField()
    evidence_files = models.FileField(upload_to='jobs/disputes/', blank=True, null=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    admin_decision = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dispute: {self.job.title}"
