from django import template

register = template.Library()

@register.filter
def split(value, arg=','):
    """String ni belgilangan ajratuvchi bo'yicha bo'laklar ro'yxatiga ajratadi."""
    return [s.strip() for s in str(value).split(arg) if s.strip()]

@register.filter
def strip(value):
    """String boshidagi va oxiridagi bo'shliqlarni olib tashlaydi."""
    return str(value).strip()

@register.filter
def get_item(dictionary, key):
    """Lug'atdan kalit bo'yicha qiymat olish."""
    return dictionary.get(key)

@register.filter
def get_options_dict(question):
    """TestQuestion ob'ektidan variantlarni ro'yxat (tuple) ko'rinishida qaytaradi."""
    return [
        ('a', question.option_a),
        ('b', question.option_b),
        ('c', question.option_c),
        ('d', question.option_d),
    ]
@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
