"""
تنظیمات اصلی پلتفرم مانیتورینگ اتوکلاو و زباله‌سوز بیمارستانی
Hospital Autoclave & Incinerator Monitoring Platform
"""

import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-hospital-monitor-change-in-production-2024!')

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

DJANGO_APPS = [
    'jazzmin',  # باید قبل از django.contrib.admin باشه
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

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ===== Database =====
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# برای Production از PostgreSQL استفاده کن:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME', default='hospital_monitor'),
#         'USER': config('DB_USER', default='postgres'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST', default='localhost'),
#         'PORT': config('DB_PORT', default='5432'),
#     }
# }

# ===== Redis & Channels =====
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

# ===== Celery =====
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tehran'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# ===== MQTT تنظیمات =====
MQTT_BROKER_HOST = config('MQTT_BROKER_HOST', default='localhost')
MQTT_BROKER_PORT = config('MQTT_BROKER_PORT', default=1883, cast=int)
MQTT_USERNAME = config('MQTT_USERNAME', default='')
MQTT_PASSWORD = config('MQTT_PASSWORD', default='')
MQTT_TOPIC_PREFIX = config('MQTT_TOPIC_PREFIX', default='hospital/devices')

# ===== SMS تنظیمات (Kavenegar) =====
KAVENEGAR_API_KEY = config('KAVENEGAR_API_KEY', default='')
ALERT_SMS_NUMBERS = config('ALERT_SMS_NUMBERS', default='').split(',')

# ===== Email =====
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===== REST Framework =====
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
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:8000'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# ===== Jazzmin Admin تنظیمات =====
JAZZMIN_SETTINGS = {
    'site_title': 'مانیتورینگ بیمارستان',
    'site_header': 'پنل مدیریت تجهیزات بیمارستانی',
    'site_brand': '🏥 Hospital Monitor',
    'welcome_sign': 'خوش آمدید - سیستم مانیتورینگ اتوکلاو و زباله‌سوز',
    'copyright': 'Hospital Monitoring System',
    'language_chooser': False,
    'show_sidebar': True,
    'navigation_expanded': True,
    'hide_apps': [],
    'hide_models': [],
    'icons': {
        'auth': 'fas fa-users-cog',
        'auth.user': 'fas fa-user',
        'apps.devices': 'fas fa-microchip',
        'apps.monitoring': 'fas fa-chart-line',
        'apps.energy': 'fas fa-bolt',
        'apps.costs': 'fas fa-money-bill-wave',
        'apps.alerts': 'fas fa-bell',
        'apps.waste': 'fas fa-trash-alt',
        'apps.reports': 'fas fa-file-alt',
    },
    'default_icon_parents': 'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-circle',
    'related_modal_active': False,
    'custom_css': None,
    'custom_js': None,
    'use_google_fonts_cdn': False,
    'show_ui_builder': False,
    'order_with_respect_to': [
        'apps.devices', 'apps.monitoring', 'apps.energy',
        'apps.costs', 'apps.waste', 'apps.alerts', 'apps.reports',
    ],
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text': False,
    'footer_small_text': False,
    'body_small_text': False,
    'brand_small_text': False,
    'brand_colour': 'navbar-success',
    'accent': 'accent-teal',
    'navbar': 'navbar-dark',
    'no_navbar_border': False,
    'navbar_fixed': True,
    'layout_boxed': False,
    'footer_fixed': False,
    'sidebar_fixed': True,
    'sidebar': 'sidebar-dark-success',
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent': False,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': False,
    'theme': 'default',
    'dark_mode_theme': None,
    'button_classes': {
        'primary': 'btn-primary',
        'secondary': 'btn-secondary',
        'info': 'btn-info',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-success',
    },
}

# ===== ضرایب محاسباتی =====
# ضریب کربن شبکه برق ایران
CARBON_FACTOR_KG_PER_KWH = 0.592

# محدوده‌های عملکرد اتوکلاو استاندارد
AUTOCLAVE_TEMP_MIN = 121  # سانتیگراد
AUTOCLAVE_TEMP_MAX = 134  # سانتیگراد
AUTOCLAVE_PRESSURE_MIN = 1.0  # بار
AUTOCLAVE_PRESSURE_MAX = 2.2  # بار

# محدوده‌های عملکرد زباله‌سوز
INCINERATOR_TEMP_MIN = 850   # سانتیگراد
INCINERATOR_TEMP_MAX = 1200  # سانتیگراد

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
