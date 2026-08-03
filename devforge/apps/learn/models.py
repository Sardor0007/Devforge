from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='📚') # Emoji or Icon class

    def __str__(self):
        return self.name

class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_approved = models.BooleanField(default=True)  # Admin tomonidan tasdiqlash

    def __str__(self):
        return self.title

    @property
    def is_free(self):
        return self.price == 0

    @property
    def lesson_count(self):
        return self.lessons.count()

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='courses/videos/', null=True, blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo link")
    content = models.TextField(blank=True) # Text content/description for the lesson
    order = models.PositiveIntegerField(default=0)
    duration = models.CharField(max_length=20, blank=True) # e.g. "15:30"

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.username} -> {self.course.title}"

    @property
    def progress_percent(self):
        total = self.course.lessons.count()
        if total == 0:
            return 0
        done = self.user.lesson_progress.filter(
            lesson__course=self.course, completed=True
        ).count()
        return round((done / total) * 100)


class LessonProgress(models.Model):
    """Foydalanuvchi qaysi darslarni tugatganini kuzatish"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'lesson']

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} ({'Tugadi' if self.completed else 'Jarayonda'})"


class Comment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learn_comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.lesson.title}"
