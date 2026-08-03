"""
django-allauth adapters — Google va GitHub dan kelgan foydalanuvchini
DevForge User modeli bilan moslashtirish.

Tuzatilgan xatolar:
- GitHub ba'zan email bermaydi → fallback username@users.noreply.github.com
- pre_social_login: email bo'lmasa ham xato bermaydi
- save_user: avatar URL ni SocialProfile ga saqlaydi
- Xush kelibsiz bildirishnomasi
"""
import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

logger = logging.getLogger(__name__)


class AccountAdapter(DefaultAccountAdapter):
    """Oddiy ro'yxatdan o'tish uchun adapter"""

    def get_login_redirect_url(self, request):
        return settings.LOGIN_REDIRECT_URL

    def save_user(self, request, user, form, commit=True):
        """Foydalanuvchi saqlanganda qo'shimcha maydonlarni to'ldirish"""
        user = super().save_user(request, user, form, commit=False)
        if not user.role:
            user.role = 'developer'
        if commit:
            user.save()
        return user


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Google / GitHub orqali kirish uchun adapter"""

    def pre_social_login(self, request, sociallogin):
        """
        Social login dan oldin: agar email mavjud bo'lsa va u allaqachon
        ro'yxatdan o'tgan bo'lsa — akkauntlarni birlashtiradi.
        """
        from apps.accounts.models import User

        if sociallogin.is_existing:
            return

        # Email olish (GitHub ba'zan bermaydi)
        email = (
            sociallogin.account.extra_data.get('email')
            or (sociallogin.email_addresses[0].email if sociallogin.email_addresses else '')
        )

        if not email:
            logger.warning(
                f"SocialLogin: no email for provider={sociallogin.account.provider}, "
                f"uid={sociallogin.account.uid}"
            )
            return

        try:
            existing_user = User.objects.get(email=email)
            sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            pass

    def populate_user(self, request, sociallogin, data):
        """
        Social profildan User modelini to'ldirish:
          Google: given_name, family_name, picture
          GitHub: login, bio, company, location, avatar_url
        """
        user     = super().populate_user(request, sociallogin, data)
        provider = sociallogin.account.provider
        extra    = sociallogin.account.extra_data

        user.role = 'developer'

        # Ensure first_name / last_name are never None (NOT NULL DB constraint)
        if not user.first_name:
            user.first_name = ''
        if not user.last_name:
            user.last_name = ''

        if provider == 'google':
            user.first_name = (extra.get('given_name') or data.get('first_name') or user.first_name or '')
            user.last_name  = (extra.get('family_name') or data.get('last_name') or user.last_name or '')
            picture = extra.get('picture', '')
            if picture:
                user._social_avatar = picture

        elif provider == 'github':
            gh_login  = extra.get('login', '') or ''
            bio       = extra.get('bio', '') or ''
            location  = extra.get('location', '') or ''

            # Parse name from GitHub "name" field if first/last_name still empty
            if not user.first_name and not user.last_name:
                gh_name = extra.get('name', '') or ''
                parts = gh_name.split(' ', 1)
                user.first_name = parts[0] if parts else ''
                user.last_name  = parts[1] if len(parts) > 1 else ''

            # GitHub username → Django username (agar bo'sh bo'lsa)
            if gh_login and not user.username:
                user.username = gh_login

            if bio:
                user.bio = bio[:500]
            if location and hasattr(user, 'location'):
                user.location = location[:100]

            # Avatar
            avatar_url = extra.get('avatar_url', '')
            if avatar_url:
                user._social_avatar = avatar_url

            # GitHub email bo'lmasa noreply manzil yaratish
            if not user.email and gh_login:
                user.email = f"{gh_login}@users.noreply.github.com"
                logger.info(f"GitHub user '{gh_login}' has no public email — using noreply fallback")

        # Final safety guard — these fields must never be None
        user.first_name = user.first_name or ''
        user.last_name  = user.last_name  or ''

        return user


    def save_user(self, request, sociallogin, form=None):
        """Social foydalanuvchini saqlash va qo'shimcha ma'lumotlarni yangilash"""
        # Final safety: ensure NOT NULL fields are never None before DB write
        u = sociallogin.user
        u.first_name = u.first_name or ''
        u.last_name  = u.last_name  or ''
        if not u.role:
            u.role = 'developer'

        user = super().save_user(request, sociallogin, form)

        # Avatar URL ni SocialProfile ga saqlash
        avatar_url = getattr(user, '_social_avatar', None)
        provider   = sociallogin.account.provider
        extra      = sociallogin.account.extra_data

        try:
            from apps.accounts.models import SocialProfile
            profile_data = {'provider': provider}

            if avatar_url:
                profile_data['avatar_url'] = avatar_url

            if provider == 'github':
                gh_login = extra.get('login', '')
                gh_html  = extra.get('html_url', '')
                if gh_login:
                    profile_data['github_username'] = gh_login
                if gh_html:
                    profile_data['github_url'] = gh_html
                # User.github maydonini ham yangilash
                if gh_html:
                    user.github = gh_html
                    user.save(update_fields=['github'])

            SocialProfile.objects.update_or_create(user=user, defaults=profile_data)

        except Exception as e:
            logger.warning(f"SocialProfile save error: {e}")

        # UserBalance va Subscription yaratish (yangi foydalanuvchi uchun)
        try:
            from apps.accounts.models import UserBalance, Subscription
            UserBalance.objects.get_or_create(user=user)
            Subscription.objects.get_or_create(user=user)
        except Exception as e:
            logger.warning(f"UserBalance/Subscription init error: {e}")

        # Xush kelibsiz bildirishnomasi
        try:
            from apps.notifications.service import notify
            notify(
                recipient=user,
                sender=None,
                notif_type='system',
                title='DevForge ga xush kelibsiz! 🎮',
                message='Profilingizni to\'ldiring va jamoa toping.',
                link='/auth/profile/edit/',
            )
        except Exception as e:
            logger.warning(f"Welcome notification error: {e}")

        return user

    def get_connect_redirect_url(self, request, socialaccount):
        return settings.LOGIN_REDIRECT_URL
