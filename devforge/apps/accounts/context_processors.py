from .models import SiteConfig

def site_settings(request):
    """Inject global feature flags and site configuration into template context."""
    return {
        'all_studios_enabled': SiteConfig.get_bool('all_studios_enabled', default=False)
    }

def subscription_status(request):
    """Inject the current user's subscription info into template context."""
    if request.user.is_authenticated:
        return {
            'subscription_type': request.user.subscription_type,
            'is_pro': request.user.subscription_type in ('pro', 'gold'),
            'is_studio': request.user.subscription_type in ('studio', 'platinum'),
            'is_enterprise': request.user.subscription_type == 'enterprise',
        }
    return {
        'subscription_type': 'free',
        'is_pro': False,
        'is_studio': False,
        'is_enterprise': False,
    }