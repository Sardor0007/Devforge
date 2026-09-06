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
        # 3D Modellari
        ('glb', 'GLB (.glb)'),
        ('gltf', 'GLTF (.gltf, .zip)'),
        ('obj', 'Wavefront OBJ (.obj)'),
        ('fbx', 'FBX (.fbx)'),
        ('blend', 'Blender (.blend)'),
        # 2D & Teksturalar
        ('png', 'PNG Rasm (.png)'),
        ('jpg', 'JPEG Rasm (.jpg, .jpeg)'),
        ('tga', 'TGA Tekstura (.tga)'),
        ('psd', 'Photoshop (.psd)'),
        # Audio
        ('mp3', 'MP3 Audio (.mp3)'),
        ('wav', 'WAV Audio (.wav)'),
        ('ogg', 'OGG Audio (.ogg)'),
        # Paket & Arxiv
        ('zip', 'ZIP Arxiv (.zip, .rar, .7z)'),
        ('unitypackage', 'Unity Paket (.unitypackage)'),
        ('other', 'Boshqa format'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assets')
    category = models.ForeignKey(AssetCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='assets/files/')
    thumbnail = models.ImageField(upload_to='assets/thumbs/', blank=True, null=True)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='other')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    tags = models.CharField(max_length=300, blank=True, help_text="Vergul bilan ajrating")
    downloads = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_assets', blank=True)
    only_for_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='private_offers', help_text="Faqat ushbu foydalanuvchi ko'ra oladi")
    is_approved = models.BooleanField(default=False, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    rejection_reason = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_assets')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_rejected(self):
        return self.status == 'rejected'

    @property
    def file_extension(self):
        if self.file and hasattr(self.file, 'name'):
            import os
            return os.path.splitext(self.file.name)[1].lower()
        return ''

    @property
    def file_size_display(self):
        try:
            if self.file and hasattr(self.file, 'size'):
                bytes_size = self.file.size
                if bytes_size >= 1024 * 1024:
                    return f"{bytes_size / (1024 * 1024):.1f} MB"
                elif bytes_size >= 1024:
                    return f"{bytes_size / 1024:.1f} KB"
                return f"{bytes_size} B"
        except Exception:
            pass
        return "Noma'lum"

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
