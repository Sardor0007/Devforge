from .models import SiteConfig
from .studios import get_studios_context

def site_settings(request):
    """Inject global feature flags and site configuration into template context."""
    return get_studios_context()

def subscription_status(request):
    """Inject the current user's subscription info into template context."""
    res = get_studios_context()
    if request.user.is_authenticated:
        res.update({
            'subscription_type': request.user.subscription_type,
            'is_pro': request.user.subscription_type in ('pro', 'gold'),
            'is_studio': request.user.subscription_type in ('studio', 'platinum'),
            'is_enterprise': request.user.subscription_type == 'enterprise',
        })
    else:
        res.update({
            'subscription_type': 'free',
            'is_pro': False,
            'is_studio': False,
            'is_enterprise': False,
        })
    return res