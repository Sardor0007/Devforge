from .models import SiteConfig

def site_settings(request):
    """Inject global feature flags and site configuration into template context."""
    return {
        'all_studios_enabled': SiteConfig.get_bool('all_studios_enabled', default=False)
    }
