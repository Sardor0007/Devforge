from django import forms
from .models import Project, ProjectRole, Task


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'genre', 'status', 'visibility', 'thumbnail', 'tech_stack', 'max_members']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Loyiha nomi'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 5}),
            'genre': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'visibility': forms.Select(attrs={'class': 'form-input'}),
            'tech_stack': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Unity, Blender, Python...'}),
            'max_members': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class ProjectRoleForm(forms.ModelForm):
    class Meta:
        model = ProjectRole
        fields = ['role_type', 'description', 'required_skills']
        widgets = {
            'role_type': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'required_skills': forms.TextInput(attrs={'class': 'form-input'}),
        }


class TaskForm(forms.ModelForm):
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            from apps.accounts.models import User
            member_ids = project.members.filter(is_approved=True).values_list('user_id', flat=True)
            self.fields['assigned_to'].queryset = User.objects.filter(
                id__in=list(member_ids) + [project.creator_id]
            )

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'assigned_to', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'priority': forms.Select(attrs={'class': 'form-input'}),
            'assigned_to': forms.Select(attrs={'class': 'form-input'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }
