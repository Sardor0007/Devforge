import os
from django import forms
from .models import Asset

class AssetUploadForm(forms.ModelForm):
    FORMAT_EXTENSIONS = {
        'glb': ['.glb'],
        'gltf': ['.gltf', '.bin', '.zip'],
        'obj': ['.obj', '.mtl', '.zip'],
        'fbx': ['.fbx', '.zip'],
        'blend': ['.blend'],
        'png': ['.png'],
        'jpg': ['.jpg', '.jpeg'],
        'tga': ['.tga'],
        'psd': ['.psd'],
        'mp3': ['.mp3'],
        'wav': ['.wav'],
        'ogg': ['.ogg'],
        'zip': ['.zip', '.rar', '.7z'],
        'unitypackage': ['.unitypackage'],
        'other': None,
    }

    DANGEROUS_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.sh', '.bash', '.vbs', '.scr', '.msi', '.pif', '.com', '.php', '.asp', '.aspx', '.jsp'
    }

    class Meta:
        model = Asset
        fields = ['title', 'description', 'category', 'format', 'file', 'thumbnail', 'price', 'tags', 'only_for_user']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masalan: Cyberpunk Low-Poly Character'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': "Aktiv haqida batafsil ma'lumot..."}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'format': forms.Select(attrs={'class': 'form-input', 'id': 'id_format'}),
            'file': forms.FileInput(attrs={'class': 'form-input', 'id': 'id_file'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'tags': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'character, fantasy, lowpoly'}),
            'only_for_user': forms.Select(attrs={'class': 'form-input'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            if ext in self.DANGEROUS_EXTENSIONS:
                raise forms.ValidationError("Xavfsizlik talablariga ko'ra ushbu turdagi (.exe, script) fayllarni yuklash taqiqlangan.")
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

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        fmt = cleaned_data.get('format')

        if file and fmt:
            ext = os.path.splitext(file.name)[1].lower()
            allowed = self.FORMAT_EXTENSIONS.get(fmt)

            if allowed and ext not in allowed:
                format_display = dict(Asset.FORMAT_CHOICES).get(fmt, fmt.upper())
                allowed_str = ", ".join(allowed)
                self.add_error(
                    'file',
                    f"Fayl formati mos kelmadi! Siz '{format_display}' formatini tanlagansiz, ammo yuklangan fayl kengaytmasi: '{ext}'. Ruxsat etilgan kengaytmalar: {allowed_str}."
                )
        return cleaned_data
