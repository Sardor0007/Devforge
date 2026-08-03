from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Skill, PortfolioItem


from django.contrib.auth import authenticate

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email manzilingiz', 'class': 'form-input'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Foydalanuvchi nomi', 'class': 'form-input'})
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ism', 'class': 'form-input'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Familiya', 'class': 'form-input'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=False,
        initial='developer',
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Parol', 'class': 'form-input'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Parolni tasdiqlang', 'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'role', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Email yoki Username', 'class': 'form-input', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Parol', 'class': 'form-input'})
    )

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email and password:
            user_to_auth = username_or_email
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email__iexact=username_or_email)
                    user_to_auth = user_obj.username
                except (User.DoesNotExist, User.MultipleObjectsReturned):
                    pass

            self.user_cache = authenticate(
                self.request,
                username=user_to_auth,
                password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'location', 'website', 'github', 'avatar', 'role']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'website': forms.URLInput(attrs={'class': 'form-input'}),
            'github': forms.URLInput(attrs={'class': 'form-input'}),
            'role': forms.Select(attrs={'class': 'form-input'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            from apps.validators import validate_file_magic
            validate_file_magic(avatar)
            from apps.image_utils import convert_to_webp
            avatar = convert_to_webp(avatar, max_width=400, quality=85)
        return avatar


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masalan: Unity, Blender'}),
            'level': forms.Select(attrs={'class': 'form-input'}),
        }


class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['title', 'description', 'item_type', 'file', 'url', 'thumbnail']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'item_type': forms.Select(attrs={'class': 'form-input'}),
            'url': forms.URLInput(attrs={'class': 'form-input'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            from apps.validators import validate_file_magic
            validate_file_magic(file)
            name = getattr(file, 'name', '').lower()
            import os
            ext = os.path.splitext(name)[1].lstrip('.')
            if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                from apps.image_utils import convert_to_webp
                file = convert_to_webp(file, max_width=1200, quality=80)
        return file

    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        if thumbnail:
            from apps.validators import validate_file_magic
            validate_file_magic(thumbnail)
            from apps.image_utils import convert_to_webp
            thumbnail = convert_to_webp(thumbnail, max_width=800, quality=80)
        return thumbnail
