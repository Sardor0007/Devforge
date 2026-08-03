from django import forms
from .models import Asset

class AssetUploadForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['title', 'description', 'category', 'file', 'thumbnail', 'format', 'price', 'tags', 'only_for_user']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'format': forms.Select(attrs={'class': 'form-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'tags': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'character, fantasy, lowpoly'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            from apps.validators import validate_file_magic
            validate_file_magic(file)
        return file

    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        if thumbnail:
            from apps.validators import validate_file_magic
            validate_file_magic(thumbnail)
            from apps.image_utils import convert_to_webp
            thumbnail = convert_to_webp(thumbnail, max_width=800, quality=80)
        return thumbnail
