from django.db import models
from apps.accounts.models import User

class Service(models.Model):
    CATEGORY_CHOICES = [
        ('3d_modeling', '3D Modeling'),
        ('game_dev', 'O\'yin Ishlab Chiqish'),
        ('ui_design', 'UI/UX Dizayn'),
        ('programming', 'Dasturlash'),
        ('animation', 'Animatsiya'),
        ('sound', 'Musiqa / Ovoz'),
        ('consulting', 'Maslahat'),
        ('other', 'Boshqa'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_days = models.PositiveIntegerField(default=3)
    thumbnail = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.seller.username} - {self.title}"

    @property
    def avg_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    @property
    def review_count(self):
        return self.reviews.count()


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('active', 'Bajarilmoqda'),
        ('completed', 'Bajarildi'),
        ('cancelled', 'Bekor qilindi'),
        ('disputed', 'Munozarali'),
    ]
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_placed')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    requirements = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.pk} {self.buyer.username} → {self.service.title}"


class Review(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['service', 'reviewer']

    def __str__(self):
        return f"{self.reviewer.username} → {self.service.title}: {self.rating}★"
