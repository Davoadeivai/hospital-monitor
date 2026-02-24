"""
تنظیمات مخصوص Render.com — نسخه رایگان بدون Redis
"""
import os
import dj_database_url
from .settings import *

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-change-in-production')

ALLOWED_HOSTS = ['*']

# ── CSRF ─────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://hospital-monitor-9f8z.onrender.com',
]
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ── Database — PostgreSQL ─────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }

# ── Channels — بدون Redis از InMemory استفاده میکنه ───────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# ── Celery — غیرفعال در نسخه رایگان ──────────────────────
CELERY_TASK_ALWAYS_EAGER = True

# ── Static ───────────────────────────────────────────────
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

CORS_ALLOW_ALL_ORIGINS = True
