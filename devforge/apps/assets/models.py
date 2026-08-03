## models.py
from django.db import models
from apps.accounts.models import User


class AssetCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='📦')

    def __str__(self):
        return self.name


class Asset(models.Model):
    FORMAT_CHOICES = [
        ('glb', 'GLB'),
        ('gltf', 'GLTF'),
        ('obj', 'OBJ'),
        ('fbx', 'FBX'),
        ('png', 'PNG Texture'),
        ('other', 'Boshqa'),
    ]
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assets')
    category = models.ForeignKey(AssetCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='assets/files/')
    thumbnail = models.ImageField(upload_to='assets/thumbs/', blank=True, null=True)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='other')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    tags = models.CharField(max_length=300, blank=True, help_text="Vergul bilan ajrating")
    downloads = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_assets', blank=True)
    only_for_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='private_offers', help_text="Faqat ushbu foydalanuvchi ko'ra oladi")
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_free(self):
        return self.price == 0

    @property
    def like_count(self):
        return self.likes.count()


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'asset']

    def __str__(self):
        return f"{self.user.username} savati: {self.asset.title}"


class PurchasedAsset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_assets')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    price_paid = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'asset']

    def __str__(self):
        return f"{self.user.username} sotib oldi: {self.asset.title}"
