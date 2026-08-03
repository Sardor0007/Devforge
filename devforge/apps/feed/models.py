from django.db import models
from apps.accounts.models import User


class Post(models.Model):
    POST_TYPES = [
        ('text',    '📝 Matn'),
        ('image',   '🖼️ Rasm'),
        ('video',   '🎥 Video'),
        ('snippet', '💻 Kod Snippet'),
        ('project', '🚀 Loyiha ulashish'),
        ('asset',   '📦 Aktiv ulashish'),
    ]
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    post_type  = models.CharField(max_length=20, choices=POST_TYPES, default='text')
    content    = models.TextField()
    image      = models.ImageField(upload_to='feed/images/', blank=True, null=True)
    video      = models.FileField(upload_to='feed/videos/', blank=True, null=True)
    code       = models.TextField(blank=True)
    code_lang  = models.CharField(max_length=30, blank=True, default='python')
    tags       = models.ManyToManyField('tags.Tag', blank=True, related_name='posts')
    is_public  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['post_type']),
            models.Index(fields=['is_public', '-created_at']),
        ]

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    def is_liked_by(self, user):
        return self.likes.filter(user=user).exists()


class PostLike(models.Model):
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'user']
        indexes = [
            models.Index(fields=['post', 'user']),
        ]


class Comment(models.Model):
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(User, on_delete=models.CASCADE)
    content    = models.TextField(max_length=1000)
    parent     = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]

    def __str__(self):
        return f"{self.author.username}: {self.content[:40]}"


class Follow(models.Model):
    follower   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'following']
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
        ]
