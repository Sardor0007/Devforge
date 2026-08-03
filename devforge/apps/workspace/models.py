from django.db import models
from apps.accounts.models import User
from apps.projects.models import Project

# ─── MODELS ──────────────────────────────────────────────────────────────────
class Workspace(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='workspace')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Workspace: {self.project.title}"


class WorkspaceFile(models.Model):
    workspace  = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='files')
    name       = models.CharField(max_length=255)
    path       = models.CharField(max_length=1000, default='/')
    content      = models.TextField(blank=True)
    binary_file  = models.FileField(upload_to='workspace_files/', null=True, blank=True)
    language     = models.CharField(max_length=50, default='python')
    is_folder    = models.BooleanField(default=False)
    file_size    = models.IntegerField(default=0)           # bytes
    github_sha   = models.CharField(max_length=40, blank=True)  # GitHub blob sha
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_folder', 'path', 'name']

    def __str__(self):
        return f"{self.workspace.project.title}/{self.path}/{self.name}"

    def full_path(self):
        if self.path == '/':
            return f'/{self.name}'
        return f'{self.path}/{self.name}'

    def extension(self):
        if self.is_folder:
            return 'folder'
        parts = self.name.rsplit('.', 1)
        return parts[-1].lower() if len(parts) > 1 else ''


class ChatRoom(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='chat_room')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat: {self.project.title}"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:40]}"
