"""
تنظیمات مخصوص Render.com
نسخه کامل — با PostgreSQL و Static Files
"""
import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── امنیت ────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-now')
DEBUG = False
ALLOWED_HOSTS = ['*']

# ── اپلیکیشن‌ها ───────────────────────────────────────────
DJANGO_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'channels',
    'corsheaders',
    'django_celery_beat',
]
LOCAL_APPS = [
    'apps.devices',
    'apps.monitoring',
    'apps.energy',
    'apps.costs',
    'apps.reports',
    'apps.alerts',
    'apps.waste',
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ── Middleware ────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
ASGI_APPLICATION = 'config.asgi.application'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.global_context',
            ],
        },
    },
]

# ── دیتابیس ───────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── Channels ──────────────────────────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# ── Celery ────────────────────────────────────────────────
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ── Static Files ──────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── CSRF ─────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://hospital-monitor-9f8z.onrender.com',
]
CSRF_COOKIE_SECURE      = True
SESSION_COOKIE_SECURE   = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ── تنظیمات عمومی ────────────────────────────────────────
LANGUAGE_CODE      = 'fa-ir'
TIME_ZONE          = 'Asia/Tehran'
USE_I18N           = True
USE_TZ             = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL           = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── REST Framework ────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

CORS_ALLOW_ALL_ORIGINS  = True
CORS_ALLOW_CREDENTIALS  = True

# ── ضرایب محاسباتی ───────────────────────────────────────
CARBON_FACTOR_KG_PER_KWH = 0.592
AUTOCLAVE_TEMP_MIN       = 121
AUTOCLAVE_TEMP_MAX       = 134
AUTOCLAVE_PRESSURE_MIN   = 1.0
AUTOCLAVE_PRESSURE_MAX   = 2.2
INCINERATOR_TEMP_MIN     = 850
INCINERATOR_TEMP_MAX     = 1200

# ── MQTT ─────────────────────────────────────────────────
MQTT_BROKER_HOST  = os.environ.get('MQTT_BROKER_HOST', 'localhost')
MQTT_BROKER_PORT  = int(os.environ.get('MQTT_BROKER_PORT', 1883))
MQTT_USERNAME     = os.environ.get('MQTT_USERNAME', '')
MQTT_PASSWORD     = os.environ.get('MQTT_PASSWORD', '')
MQTT_TOPIC_PREFIX = os.environ.get('MQTT_TOPIC_PREFIX', 'hospital/devices')

# ── SMS ───────────────────────────────────────────────────
KAVENEGAR_API_KEY = os.environ.get('KAVENEGAR_API_KEY', '')
ALERT_SMS_NUMBERS = os.environ.get('ALERT_SMS_NUMBERS', '').split(',')

# ── Jazzmin ───────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    'site_title':   'صنایع پزشکی آتیه',
    'site_header':  'آتیه مانیتور',
    'site_brand':   '⚕️ Atieh Medical',
    'welcome_sign': 'خوش آمدید — سیستم مانیتورینگ صنایع پزشکی آتیه',
    'copyright':    'صنایع پزشکی آتیه',
    'show_sidebar': True,
    'navigation_expanded': True,
    'icons': {
        'auth':            'fas fa-users-cog',
        'auth.user':       'fas fa-user',
        'apps.devices':    'fas fa-microchip',
        'apps.monitoring': 'fas fa-chart-line',
        'apps.energy':     'fas fa-bolt',
        'apps.costs':      'fas fa-money-bill-wave',
        'apps.alerts':     'fas fa-bell',
        'apps.waste':      'fas fa-trash-alt',
        'apps.reports':    'fas fa-file-alt',
    },
}

JAZZMIN_UI_TWEAKS = {
    'navbar':        'navbar-dark',
    'navbar_fixed':  True,
    'sidebar':       'sidebar-dark-success',
    'sidebar_fixed': True,
    'accent':        'accent-teal',
    'brand_colour':  'navbar-success',
    'theme':         'default',
}
