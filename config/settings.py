import os
import sys
import dj_database_url
from pathlib import Path

# ==============================================================================
# Monkeypatch: Django 4.2 + Python 3.14 (Template Context __copy__ bug)
# ==============================================================================
if sys.version_info >= (3, 14):
    from django.template import context
    def _patched_context_copy(self):
        duplicate = super(context.BaseContext, self).__copy__()
        duplicate.dicts = self.dicts[:]
        return duplicate
    context.BaseContext.__copy__ = _patched_context_copy


# =====================================================
# Base
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# =====================================================
# Security
# =====================================================
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-this-immediately"
)

# اگر DEBUG=True باشد یعنی لوکال
DEBUG = os.environ.get("DEBUG", "True") == "True"

# تشخیص Render
IS_RENDER = "RENDER_EXTERNAL_HOSTNAME" in os.environ
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

# Allowed Hosts
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
if IS_RENDER and RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# =====================================================
# CSRF
# =====================================================
CSRF_TRUSTED_ORIGINS = []
if IS_RENDER and RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# =====================================================
# Applications
# =====================================================
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "corsheaders",

    "apps.devices",
    "apps.monitoring",
    "apps.energy",
    "apps.alerts",
    "apps.costs",
    "apps.waste",
    "apps.reports",
]

# =====================================================
# Middleware
# =====================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# =====================================================
# Database
# =====================================================
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# =====================================================
# Templates
# =====================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# =====================================================
# Internationalization
# =====================================================
LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

# =====================================================
# Static & Media
# =====================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =====================================================
# Security Settings
# =====================================================
if not DEBUG and IS_RENDER:
    # فقط در production واقعی HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # در لوکال همه خاموش
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None
    SECURE_HSTS_SECONDS = 0

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# =====================================================
# CORS
# =====================================================
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    if IS_RENDER and RENDER_EXTERNAL_HOSTNAME:
        CORS_ALLOWED_ORIGINS = [f"https://{RENDER_EXTERNAL_HOSTNAME}"]

# =====================================================
# REST Framework
# =====================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# =====================================================
# Email
# =====================================================
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

# =====================================================
# Default Field
# =====================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =====================================================
# Django Channels — WebSocket Layer
# =====================================================
_redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [_redis_url],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

# =====================================================
# Celery — صف پردازش پس‌زمینه
# =====================================================
CELERY_BROKER_URL = _redis_url
CELERY_RESULT_BACKEND = _redis_url
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60       # 30 دقیقه حداکثر برای هر تسک
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CELERY_BEAT_SCHEDULE = {
    # بررسی اتصال دستگاه‌ها هر ۵ دقیقه
    'check-device-connectivity': {
        'task': 'apps.monitoring.tasks.check_device_connectivity',
        'schedule': 300,  # هر ۵ دقیقه
    },
    # گزارش ماهانه — اول هر ماه ساعت ۱ بامداد
    'monthly-energy-report': {
        'task': 'apps.monitoring.tasks.generate_monthly_report',
        'schedule': 60 * 60 * 24 * 30,  # تقریبی — در production از crontab استفاده شود
    },
    # پاک‌سازی داده‌های قدیمی — هر شب ساعت ۲ بامداد
    'cleanup-old-sensor-data': {
        'task': 'apps.monitoring.tasks.cleanup_old_sensor_data',
        'schedule': 60 * 60 * 24,  # هر ۲۴ ساعت
    },
}


# =====================================================
# MQTT تنظیمات
# =====================================================
MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", 1883))
MQTT_USERNAME = os.environ.get("MQTT_USERNAME", "")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "")
MQTT_TOPIC_PREFIX = os.environ.get("MQTT_TOPIC_PREFIX", "hospital/devices")

# =====================================================
# هشدار پیامکی (Kavenegar)
# =====================================================
KAVENEGAR_API_KEY = os.environ.get("KAVENEGAR_API_KEY", "")
ALERT_SMS_NUMBERS = [
    n.strip() for n in os.environ.get("ALERT_SMS_NUMBERS", "").split(",") if n.strip()
]

# =====================================================
# Data Retention — سیاست نگه‌داری داده
# =====================================================
SENSOR_RAW_RETENTION_DAYS = int(os.environ.get("SENSOR_RAW_RETENTION_DAYS", 90))
ALERT_RETENTION_DAYS       = int(os.environ.get("ALERT_RETENTION_DAYS", 365))

# =====================================================
# Carbon Budget — بودجه ماهانه کربن (kg)
# =====================================================
CARBON_BUDGET_KG_MONTHLY = int(os.environ.get("CARBON_BUDGET_KG_MONTHLY", 500))


# =====================================================
# Logging
# =====================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "core": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}