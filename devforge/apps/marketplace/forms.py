from django import forms
from .models import Service, Order, Review

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'category', 'price', 'delivery_days', 'thumbnail']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '1'}),
            'delivery_days': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
        }

    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        if thumbnail:
            from apps.validators import validate_file_magic
            validate_file_magic(thumbnail)
            from apps.image_utils import convert_to_webp
            thumbnail = convert_to_webp(thumbnail, max_width=800, quality=80)
        return thumbnail


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['requirements']
        widgets = {
            'requirements': forms.Textarea(attrs={'class': 'form-input', 'rows': 4,
                'placeholder': 'Xizmat haqida qo\'shimcha talablar...'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }
