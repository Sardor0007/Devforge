from django.db import models
from apps.accounts.models import User


class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Rejalashtirish'),
        ('active', 'Aktiv'),
        ('completed', 'Yakunlangan'),
        ('paused', 'To\'xtatilgan'),
    ]
    VISIBILITY_CHOICES = [
        ('public', 'Ochiq'),
        ('private', 'Yopiq'),
        ('invite', 'Taklif bilan'),
    ]
    GENRE_CHOICES = [
        ('action', 'Action'),
        ('rpg', 'RPG'),
        ('strategy', 'Strategiya'),
        ('puzzle', 'Puzzle'),
        ('simulation', 'Simulyatsiya'),
        ('horror', 'Horror'),
        ('platformer', 'Platformer'),
        ('other', 'Boshqa'),
    ]

    creator     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    title       = models.CharField(max_length=200)
    description = models.TextField()
    genre       = models.CharField(max_length=30, choices=GENRE_CHOICES, default='other')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    visibility  = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    thumbnail   = models.ImageField(upload_to='projects/', blank=True, null=True)
    tech_stack  = models.ManyToManyField('tags.Tag', blank=True, related_name='projects')
    max_members = models.PositiveIntegerField(default=10)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['creator', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['visibility', 'status']),
        ]

    def __str__(self):
        return self.title

    @property
    def member_count(self):
        return self.members.filter(is_approved=True).count()

    @property
    def open_roles_count(self):
        return self.roles.filter(is_filled=False).count()


class ProjectRole(models.Model):
    ROLE_CHOICES = [
        ('developer', 'O\'yin Dasturchisi'),
        ('programmer', 'Dasturchi'),
        ('artist', '3D Rassom'),
        ('designer', 'Dizayner'),
        ('sound', 'Musiqa/Ovoz'),
        ('writer', 'Stsenariy Yozuvchi'),
        ('other', 'Boshqa'),
    ]
    project        = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='roles')
    role_type      = models.CharField(max_length=20, choices=ROLE_CHOICES)
    description    = models.TextField(blank=True)
    required_skills = models.CharField(max_length=200, blank=True)
    is_filled      = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.project.title} - {self.get_role_type_display()}"


class ProjectMember(models.Model):
    project    = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role       = models.ForeignKey(ProjectRole, on_delete=models.SET_NULL, null=True, blank=True)
    message    = models.TextField(blank=True, help_text="Ariza xabari")
    is_approved = models.BooleanField(default=False)
    joined_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['project', 'user']
        indexes = [
            models.Index(fields=['project', 'is_approved']),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.project.title}"


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'Bajarilishi kerak'),
        ('inprogress', 'Jarayonda'),
        ('done', 'Bajarildi'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Past'),
        ('medium', 'O\'rta'),
        ('high', 'Yuqori'),
    ]
    project     = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo')
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date    = models.DateField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f"{self.project.title} - {self.title}"
