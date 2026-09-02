from django.db import models
from django.core.validators import FileExtensionValidator
from apps.accounts.models import User


class AssetCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default="cube")

    def __str__(self):
        return self.name


class Asset3D(models.Model):
    """Foydalanuvchi yuklagan 3D asset (GLB/GLTF/OBJ)"""
    FORMAT_CHOICES = [
        ("glb",  "GLB (Binary glTF)"),
        ("gltf", "glTF"),
        ("obj",  "OBJ"),
    ]

    creator     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="studio_3d_assets")
    category    = models.ForeignKey(AssetCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file        = models.FileField(
        upload_to="studio_3d/models/",
        validators=[FileExtensionValidator(allowed_extensions=["glb", "gltf", "obj"])],
    )
    thumbnail   = models.ImageField(upload_to="studio_3d/thumbs/", blank=True, null=True)
    format      = models.CharField(max_length=10, choices=FORMAT_CHOICES, default="glb")
    file_size   = models.PositiveIntegerField(default=0, help_text="Bytes")
    tags        = models.CharField(max_length=300, blank=True)
    download_count = models.PositiveIntegerField(default=0)
    is_public   = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "3D Asset"
        verbose_name_plural = "3D Assets"

    def __str__(self):
        return f"{self.title} ({self.format.upper()})"

    def save(self, *args, **kwargs):
        # Fayl hajmini avtomatik saqlash
        if self.file and hasattr(self.file, "size"):
            self.file_size = self.file.size
        # Formatni fayldan aniqlash
        if self.file and not self.format:
            ext = self.file.name.lower().split(".")[-1]
            if ext in ("glb", "gltf", "obj"):
                self.format = ext
        super().save(*args, **kwargs)

    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def is_gltf_family(self):
        return self.format in ("glb", "gltf")


class Scene3D(models.Model):
    """To'liq 3D sahna — tahrirlash uchun"""
    TEMPLATE_CHOICES = [
        ("empty",    "Bo'sh sahna"),
        ("showcase", "Showcase (Vitrina)"),
        ("terrain",  "Terrain"),
        ("room",     "Xona (Room)"),
        ("space",    "Kosmik muhit"),
        ("nature",   "Tabiat"),
        ("abstract", "Abstrakt"),
    ]

    creator    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scenes_3d")
    title      = models.CharField(max_length=200, default="Untitled Scene")
    template   = models.CharField(max_length=30, choices=TEMPLATE_CHOICES, default="empty")
    # JSON: { objects: [...], lights: [...], camera: {...}, env: {...} }
    scene_data = models.JSONField(default=dict, blank=True)
    thumbnail  = models.ImageField(upload_to="studio_3d/scene_thumbs/", blank=True, null=True)
    is_public  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    @property
    def object_count(self):
        return len(self.scene_data.get("objects", []))

    @property
    def thumbnail_url(self):
        return self.thumbnail.url if self.thumbnail else None