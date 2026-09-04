import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production-!!!')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS: env var + Render.com auto-detect
_allowed = os.environ.get('ALLOWED_HOSTS', 'localhost 127.0.0.1').split()
_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')  # Render.com sets this
if _render_host:
    _allowed.append(_render_host)
if DEBUG:
    _allowed += ['.ngrok-free.dev', '.ngrok.io', 'localhost', '127.0.0.1']
ALLOWED_HOSTS = _allowed

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = []
if _render_host:
    CSRF_TRUSTED_ORIGINS.append(f'https://{_render_host}')
if DEBUG:
    CSRF_TRUSTED_ORIGINS += [
        'https://*.ngrok-free.dev',
        'https://*.ngrok.io',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Initialize environment variables
try:
    import environ
    env = environ.Env(
        DEBUG=(bool, False),
        CELERY_BROKER_URL=(str, 'redis://localhost:6379/0'),
        CELERY_RESULT_BACKEND=(str, 'redis://localhost:6379/0'),
        STRIPE_PUBLIC_KEY=(str, ''),
        STRIPE_SECRET_KEY=(str, ''),
        STRIPE_WEBHOOK_SECRET=(str, ''),
        REDIS_URL=(str, 'redis://localhost:6379/1'),
    )
    # Read .env file if it exists
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
except ImportError:
    # Fallback to os.environ if django-environ is not installed
    def env(key, default=None):
        return os.environ.get(key, default)

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',          # allauth uchun majburiy

    # django-allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',

    # DevForge apps
    'apps',                  # templatetags uchun
    'apps.accounts',
    'apps.projects',
    'apps.assets',
    'apps.marketplace',
    'apps.workspace',
    'apps.notifications',
    'apps.analytics',
    'apps.messaging',
    'apps.feed',
    'apps.jobs',
    'apps.learn',
    'apps.payments',
    'apps.tags',
    'apps.assessment',
    'apps.challenges',
    'apps.jams',
    'apps.studio',
    'apps.studio_3d',
    'apps.image_editor',
    'apps.audio_lab',
    'apps.video_lab',
    'apps.world_builder',
    'apps.game_engine',
    'apps.api',              # REST API app
    'rest_framework',
    'rest_framework_simplejwt',
    'apps.integrations',
    'corsheaders',
    'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # allauth middleware
    'apps.accounts.middleware.SubscriptionMiddleware',
]

ROOT_URLCONF = 'devforge.urls'

# ── I18N & LANGUAGES (uz / ru / en) ──────────────────────────────────────────
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('uz', "O'zbekcha"),
    ('ru', 'Русский'),
    ('en', 'English'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.template.context_processors.i18n',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'apps.accounts.context_processors.site_settings',
        'apps.accounts.context_processors.subscription_status',
    ]},
}]

# Upload size limits for 3D Studio Textures (Base64)
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
JSON_EDITOR_JS = 'https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/9.10.0/jsoneditor.min.js'
ASGI_APPLICATION = 'devforge.asgi.application'

# ── CHANNEL LAYERS (WebSockets) ──────────────────────────────────────────────
# Lokalda Redis yo'q bo'lsa ham ishlashi uchun InMemory fallback qo'shildi
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Production yoki Redis o'rnatilgan bo'lsa
REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL and not DEBUG:
    CHANNEL_LAYERS["default"] = {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
            "capacity": 1500,
            "expiry": 60,
        },
    }

# ── CELERY SOZLAMALARI ────────────────────────────────────────────────────────
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tashkent'

# ── CELERY BEAT (Scheduled Tasks) ────────────────────────────────────────────
try:
    from celery.schedules import crontab
    CELERY_BEAT_SCHEDULE = {
        # Har 2 soatda topshirilgan 3+ kunlik ishlarni avtomatik tasdiqlash
        'auto-approve-deliveries': {
            'task': 'apps.tasks.auto_approve_old_deliveries',
            'schedule': crontab(minute=0, hour='*/2'),
        },
        # Har kuni ertalab 6:00 da barcha workspace larni diskka sinxronlash
        'sync-all-workspaces': {
            'task': 'apps.tasks.sync_all_workspaces',
            'schedule': crontab(minute=0, hour=6),
        },
        # Har dushanba 00:00 da haftalik reytingni yangilash
        'update-weekly-leaderboard': {
            'task': 'apps.tasks.update_weekly_leaderboard',
            'schedule': crontab(minute=0, hour=0, day_of_week='monday'),
        },
        # Har kuni yarim tunda rate limitlarni tozalash
        'cleanup-expired-rate-limits': {
            'task': 'apps.tasks.cleanup_expired_rate_limits',
            'schedule': crontab(minute=0, hour=0),
        },
    }
except ImportError:
    CELERY_BEAT_SCHEDULE = {}

DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
if DATABASE_URL:
    try:
        import dj_database_url
        import socket
        from urllib.parse import urlparse

        parsed = urlparse(DATABASE_URL)
        use_fallback = False

        if parsed.hostname:
            try:
                # Test whether database host actually resolves in DNS
                socket.gethostbyname(parsed.hostname)
            except (socket.gaierror, socket.herror, Exception) as dns_err:
                print(f"[CRITICAL WARNING] DATABASE_URL host '{parsed.hostname}' could not be resolved ({dns_err}).")
                print("[FALLBACK] Automatically switching to SQLite to keep DevForge online.")
                use_fallback = True

        if not use_fallback:
            DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
        else:
            DATABASES = {'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }}
    except Exception as e:
        print(f"[DATABASE CONFIG ERROR] {e}. Falling back to SQLite.")
        DATABASES = {'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }}
else:
    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}

# ── AUTH ──────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL     = 'accounts.User'
LOGIN_URL           = '/auth/login/'
LOGIN_REDIRECT_URL  = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ── ALLAUTH SOZLAMALARI (allauth v65+) ───────────────────────────────────────
SITE_ID = 1

# allauth v65+ yangi API:
ACCOUNT_LOGIN_METHODS      = {'email'}
ACCOUNT_SIGNUP_FIELDS      = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'optional'    # 'mandatory' | 'optional' | 'none'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRM    = True
ACCOUNT_USERNAME_MIN_LENGTH       = 3
ACCOUNT_UNIQUE_EMAIL              = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_ADAPTER                   = 'apps.accounts.adapters.AccountAdapter'
SOCIALACCOUNT_ADAPTER             = 'apps.accounts.adapters.SocialAccountAdapter'
SOCIALACCOUNT_AUTO_SIGNUP         = True
SOCIALACCOUNT_LOGIN_ON_GET        = False   # GET orqali avtomatik kirish o'chirildi
# OAuth orqali kelgan email ni qayta verify qilmang
SOCIALACCOUNT_EMAIL_VERIFICATION  = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED      = False

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret':    os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key':       '',
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'FETCH_USERINFO': True,
    },
    'github': {
        'APP': {
            'client_id': os.environ.get('GITHUB_CLIENT_ID', ''),
            'secret':    os.environ.get('GITHUB_CLIENT_SECRET', ''),
            'key':       '',
        },
        'SCOPE':       ['read:user', 'user:email'],
        'AUTH_PARAMS': {},
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── TIL VA VAQT ───────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'uz'
TIME_ZONE     = 'Asia/Tashkent'
USE_I18N      = True
USE_TZ        = True

# ── FAYLLAR ───────────────────────────────────────────────────────────────────
STATIC_URL          = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT         = BASE_DIR / 'staticfiles'
STATICFILES_DIRS    = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
MEDIA_URL           = '/media/'
MEDIA_ROOT          = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── EMAIL ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'DevForge <noreply@devforge.uz>')
SITE_NAME           = 'DevForge'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ── PRODUCTION XAVFSIZLIK ────────────────────────────────────────────────────
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER      = True
    SECURE_CONTENT_TYPE_NOSNIFF    = True
    SECURE_HSTS_SECONDS            = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT            = True
    SESSION_COOKIE_SECURE          = True
    CSRF_COOKIE_SECURE             = True
    X_FRAME_OPTIONS                = 'DENY'
    SECURE_HSTS_PRELOAD             = True
    SESSION_COOKIE_SAMESITE         = 'Lax'
    CSRF_COOKIE_SAMESITE            = 'Lax'

# ── BOSHQA ───────────────────────────────────────────────────────────────────
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024
SESSION_COOKIE_AGE          = 60 * 60 * 8    # 8 soat (30 kun emas)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True        # Brauzer yopilganda session tugaydi
SESSION_SAVE_EVERY_REQUEST  = False
ANTHROPIC_API_KEY           = os.environ.get('ANTHROPIC_API_KEY', '')

# ── STRIPE SOZLAMALARI ────────────────────────────────────────────────────────
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')

# ── RATE LIMITING ─────────────────────────────────────────────────────────────
RATELIMIT_ENABLE = not DEBUG
RATELIMIT_USE_CACHE = 'default'

# ── CACHES ────────────────────────────────────────────────────────────────────
# Redis kesh tizimi (faqat Redis ishlayotgan bo'lsa)
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL and not DEBUG:
    try:
        import django_redis
        CACHES = {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': REDIS_URL,
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                }
            }
        }
    except ImportError:
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
# ── REST FRAMEWORK SOZLAMALARI ────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'DevForge API',
    'DESCRIPTION': 'O\'yin dasturchilari platformasi uchun API hujjatlari',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# ── CORS SOZLAMALARI ──────────────────────────────────────────────────────────
# Local dev da barcha origin ochiq; production da faqat ruxsat etilganlar
CORS_ALLOW_ALL_ORIGINS = DEBUG

# Production uchun — Render.com va env var orqali qo'shiladigan domenlar
_cors_extra = [
    o.strip() for o in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()
]
if _render_host:
    _cors_extra.append(f'https://{_render_host}')

if not DEBUG:
    CORS_ALLOWED_ORIGINS = _cors_extra or [
        # Hech narsa ko'rsatilmasa, Render domeniga ruxsat
        f'https://{_render_host}' if _render_host else 'http://localhost:8000',
    ]

CORS_ALLOW_CREDENTIALS = True   # JWT Cookie yoki session cookie bilan ishlash

# Android / iOS / boshqa mobil ilovalar uchun zarur headerlar
from corsheaders.defaults import default_headers  # noqa
CORS_ALLOW_HEADERS = list(default_headers) + [
    'Authorization',        # JWT Bearer token uchun
    'X-CSRFToken',
    'X-Requested-With',
    'Content-Type',
    'Accept',
    'Accept-Language',
    'X-Device-Id',          # Mobil qurilma ID (ixtiyoriy)
]

CORS_ALLOW_METHODS = [
    'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',
]


# ── SIMPLE JWT SOZLAMALARI ───────────────────────────────────────────────────
from datetime import timedelta

SIMPLE_JWT = {
    # Token umrlari
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=2),      # 2 soat
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),       # 30 kun (mobil ilova uchun)
    'ROTATE_REFRESH_TOKENS':  True,                     # Har refreshda yangi refresh token
    'BLACKLIST_AFTER_ROTATION': False,                  # Blacklist app siz

    # Header
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',

    # Token tarkibi
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    # Algorithm
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'devforge',

    # Sliding tokens (ixtiyoriy)
    'SLIDING_TOKEN_LIFETIME':         timedelta(hours=2),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=30),

    # Serializer'lar
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSerializer',
    'TOKEN_VERIFY_SERIALIZER':  'rest_framework_simplejwt.serializers.TokenVerifySerializer',
}

# ── CSRF TRUSTED ORIGINS (Production) ────────────────────────────────────────
# Render.com va mobil ilovalar uchun
_render_domain = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
if _render_domain:
    CSRF_TRUSTED_ORIGINS += [f'https://{_render_domain}']
