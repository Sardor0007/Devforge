from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Markaziy plan konfiguratsiyasi — faqat shu yerda o'zgartirish kifoya
PLAN_CONFIG = {
    'free':       {'label': 'Free',       'icon': '⭐', 'color': '#94a3b8', 'bg': 'rgba(148,163,184,0.1)', 'border': 'rgba(148,163,184,0.25)'},
    'pro':        {'label': 'Pro',        'icon': '🚀', 'color': '#818cf8', 'bg': 'rgba(129,140,248,0.12)', 'border': 'rgba(129,140,248,0.3)'},
    'studio':     {'label': 'Studio',     'icon': '🏆', 'color': '#a78bfa', 'bg': 'rgba(167,139,250,0.12)', 'border': 'rgba(167,139,250,0.3)'},
    'enterprise': {'label': 'Enterprise', 'icon': '💎', 'color': '#38bdf8', 'bg': 'rgba(56,189,248,0.12)',  'border': 'rgba(56,189,248,0.3)'},
    # Eski nomlar — Pro/Studio ga yo'naltirish
    'gold':       {'label': 'Pro',        'icon': '🚀', 'color': '#818cf8', 'bg': 'rgba(129,140,248,0.12)', 'border': 'rgba(129,140,248,0.3)'},
    'platinum':   {'label': 'Studio',     'icon': '🏆', 'color': '#a78bfa', 'bg': 'rgba(167,139,250,0.12)', 'border': 'rgba(167,139,250,0.3)'},
}

def _get_plan(plan_key):
    """Plan key bo'yicha konfiguratsiyani qaytaradi, noma'lum bo'lsa free."""
    key = (plan_key or 'free').lower()
    return PLAN_CONFIG.get(key, PLAN_CONFIG['free'])


@register.simple_tag
def sub_badge(plan_key, size='normal'):
    """
    Har qanday joyda bir xil obuna badge chiqaradi.
    Ishlatish: {% load sub_tags %}  {% sub_badge user.subscription_type %}
    """
    cfg = _get_plan(plan_key)
    font = '0.72rem' if size == 'small' else '0.78rem'
    pad  = '0.2rem 0.55rem' if size == 'small' else '0.3rem 0.8rem'
    html = (
        f'<span style="display:inline-flex;align-items:center;gap:0.3rem;'
        f'font-size:{font};font-weight:700;padding:{pad};border-radius:99px;'
        f'background:{cfg["bg"]};border:1px solid {cfg["border"]};color:{cfg["color"]};">'
        f'{cfg["icon"]} {cfg["label"]}</span>'
    )
    return mark_safe(html)


@register.simple_tag
def sub_label(plan_key):
    """Faqat text: 'Free', 'Pro', 'Studio', 'Enterprise'"""
    return _get_plan(plan_key)['label']


@register.simple_tag
def sub_icon(plan_key):
    """Faqat emoji: ⭐ 🚀 🏆 💎"""
    return _get_plan(plan_key)['icon']


@register.filter
def normalize_plan(plan_key):
    """gold→pro, platinum→studio, qolganlar o'zgarmaydi"""
    mapping = {'gold': 'pro', 'platinum': 'studio'}
    return mapping.get((plan_key or '').lower(), plan_key or 'free')
