"""
تنظیمات محلی برای توسعه روی لپ‌تاپ
بدون نیاز به Redis، PostgreSQL، یا Celery

نحوه استفاده:
    set DJANGO_SETTINGS_MODULE=config.local_settings   (Windows)
    export DJANGO_SETTINGS_MODULE=config.local_settings (Linux/Mac)
"""

from .settings import *

DEBUG = True

# SQLite — نیاز به نصب ندارد
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# InMemory Channel Layer — نیاز به Redis ندارد
# WebSocket کار می‌کند ولی فقط در یک process
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# Celery غیرفعال — تسک‌ها Sync اجرا می‌شوند
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email — فقط در Console نشان بده
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# MQTT غیرفعال در حالت local
MQTT_ENABLED = False

# Jazzmin فعال
INSTALLED_APPS = [app for app in INSTALLED_APPS]

print("✅ Local Settings loaded — SQLite + InMemory Channels")
