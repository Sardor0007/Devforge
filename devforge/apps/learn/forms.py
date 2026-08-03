from django import forms
from .models import Course, Lesson

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'thumbnail', 'category', 'level', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Course Title'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'What is this course about?'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'level': forms.Select(attrs={'class': 'form-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['thumbnail'].required = False
        self.fields['description'].required = False
        self.fields['price'].required = False

    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        if thumbnail:
            from apps.validators import validate_file_magic
            validate_file_magic(thumbnail)
            from apps.image_utils import convert_to_webp
            thumbnail = convert_to_webp(thumbnail, max_width=800, quality=80)
        return thumbnail

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'video_file', 'video_url', 'content', 'order', 'duration']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Lesson Title'}),
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-input'}),
            'duration': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 10:45'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['video_file'].required = False
        self.fields['video_url'].required = False
        self.fields['content'].required = False
        self.fields['duration'].required = False

    def clean_video_file(self):
        video_file = self.cleaned_data.get('video_file')
        if video_file:
            from apps.validators import validate_file_magic
            validate_file_magic(video_file)
        return video_file
