# config/settings.py

import os
from pathlib import Path

# ────────────────────────────────────────────────
# Base Directory
# ────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ────────────────────────────────────────────────
# Security & Environment
# ────────────────────────────────────────────────
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-default-key-change-me")
DEBUG = os.environ.get("DEBUG", "True") == "True"           # در Render → False کن

ALLOWED_HOSTS = [
    '*',                                 # برای تست Render رایگان
    'hospital-monitor-9f8z.onrender.com',  # دامنه Render خودت
    '127.0.0.1',
    'localhost',
]

# ────────────────────────────────────────────────
# Installed Apps
# ────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django defaults
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "corsheaders",
    "jazzmin",

    # Your apps
    "apps.devices",
    "apps.monitoring",
    "apps.energy",
]

# ────────────────────────────────────────────────
# Middleware
# ────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # حتماً نزدیک اول
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ────────────────────────────────────────────────
# URL / WSGI / ASGI
# ────────────────────────────────────────────────
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ────────────────────────────────────────────────
# Database (SQLite برای Render رایگان)
# بعداً می‌توانی به PostgreSQL تغییر بدی
# ────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ────────────────────────────────────────────────
# Templates
# ────────────────────────────────────────────────
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

# ────────────────────────────────────────────────
# Password validation
# ────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ────────────────────────────────────────────────
# Internationalization
# ────────────────────────────────────────────────
LANGUAGE_CODE = "fa-ir"     # فارسی – اگر می‌خوای
TIME_ZONE = "Asia/Tehran"   # ایران
USE_I18N = True
USE_TZ = True

# ────────────────────────────────────────────────
# Static files (WhiteNoise + Render)
# ────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# مهم برای رفع خطای .map در collectstatic
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ('map',)

# ────────────────────────────────────────────────
# Media files
# ────────────────────────────────────────────────
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ────────────────────────────────────────────────
# CORS (برای توسعه باز – در تولید محدود کن)
# ────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ────────────────────────────────────────────────
# Default primary key field
# ────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ────────────────────────────────────────────────
# Django REST Framework
# ────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ]
}

# ────────────────────────────────────────────────
# Email (console برای توسعه)
# ────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"