from django.db import models
from django.conf import settings
from django.utils import timezone


class GameProject(models.Model):
    GENRE_CHOICES = [
        ('platformer', 'Platformer'),
        ('puzzle',     'Puzzle'),
        ('shooter',    'Shooter'),
        ('rpg',        'RPG'),
        ('arcade',     'Arcade'),
        ('adventure',  'Adventure'),
        ('strategy',   'Strategy'),
        ('other',      'Other'),
    ]

    owner       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='game_projects')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    thumbnail   = models.ImageField(upload_to='game_engine/thumbnails/', blank=True, null=True)
    genre       = models.CharField(max_length=20, choices=GENRE_CHOICES, default='other')
    is_public   = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    play_count  = models.PositiveIntegerField(default=0)
    like_count  = models.PositiveIntegerField(default=0)
    engine_version = models.CharField(max_length=10, default='1.0')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Game Project'
        verbose_name_plural = 'Game Projects'

    def __str__(self):
        return f"{self.title} ({self.owner.username})"


class GameScene(models.Model):
    project    = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='scenes')
    name       = models.CharField(max_length=100, default='Main Scene')
    order      = models.PositiveIntegerField(default=0)
    is_main    = models.BooleanField(default=False)
    # Full scene state: entities, layers, camera, settings
    scene_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Game Scene'

    def __str__(self):
        return f"{self.project.title} / {self.name}"


class GameAsset(models.Model):
    ASSET_TYPES = [
        ('sprite',  'Sprite / Image'),
        ('audio',   'Audio / Sound'),
        ('tilemap', 'Tilemap'),
        ('font',    'Font'),
        ('script',  'Script File'),
        ('other',   'Other'),
    ]
    project    = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='assets')
    name       = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES, default='sprite')
    file       = models.FileField(upload_to='game_engine/assets/')
    thumbnail  = models.ImageField(upload_to='game_engine/asset_thumbs/', blank=True, null=True)
    width      = models.PositiveIntegerField(default=0)
    height     = models.PositiveIntegerField(default=0)
    file_size  = models.PositiveIntegerField(default=0)   # bytes
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['asset_type', 'name']
        verbose_name = 'Game Asset'

    def __str__(self):
        return f"{self.name} [{self.asset_type}]"


class GameScript(models.Model):
    SCRIPT_TYPES = [
        ('behavior', 'Behavior Script'),
        ('event',    'Event Handler'),
        ('global',   'Global Script'),
    ]
    project     = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='scripts')
    name        = models.CharField(max_length=100)
    script_type = models.CharField(max_length=20, choices=SCRIPT_TYPES, default='behavior')
    code        = models.TextField(blank=True, default='// Write your game logic here\n')
    node_data   = models.JSONField(default=dict)   # visual node graph state
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Game Script'

    def __str__(self):
        return f"{self.project.title} / {self.name}"


class GameBuild(models.Model):
    project    = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='builds')
    version    = models.CharField(max_length=20, default='1.0.0')
    build_data = models.JSONField(default=dict)   # full serialized game bundle
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Game Build'

    def __str__(self):
        return f"{self.project.title} v{self.version}"


class GameLike(models.Model):
    project = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='likes')
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='game_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('project', 'user')]
        verbose_name = 'Game Like'


class GameComment(models.Model):
    project  = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='comments')
    author   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='game_comments')
    body     = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Game Comment'

    def __str__(self):
        return f"Comment by {self.author.username} on {self.project.title}"


class GamePlaySession(models.Model):
    project          = models.ForeignKey(GameProject, on_delete=models.CASCADE, related_name='play_sessions')
    player           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='play_sessions')
    started_at       = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    completed        = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Play Session'
