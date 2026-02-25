# config/settings.py
<<<<<<< HEAD
import os
from pathlib import Path

# مسیر پایه پروژه
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# تنظیمات امنیتی
# ------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = ["*"]  # در نسخه تست / رایگان برای Render

# ------------------------------
# اپ‌ها
# ------------------------------
INSTALLED_APPS = [
=======

import os
from pathlib import Path

# -----------------------------------
# Base directory
# -----------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------
# Security
# -----------------------------------
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "replace-this-with-a-secure-key")
DEBUG = True  # برای تست در Render، بعداً می‌توان False کرد
ALLOWED_HOSTS = ["*"]  # Render رایگان فقط تست، برای production دقیق‌تر تنظیم شود

# -----------------------------------
# Installed apps
# -----------------------------------
INSTALLED_APPS = [
    # اپ‌های پیش‌فرض Django
>>>>>>> 894b689 (آخرین تغییرات پروژه (رفع مشکلات Pillow، تنظیمات Render و ...))
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

<<<<<<< HEAD
    # اپ‌های شما
    "rest_framework",
    "corsheaders",
    "jazzmin",
]

# ------------------------------
# Middleware
# ------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # مهم: قبل از StaticFilesMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "corsheaders.middleware.CorsMiddleware",
=======
    # اپ‌های ثالث
    "rest_framework",
    "corsheaders",
    "jazzmin",

    # اپ‌های خودت
    "apps.devices",
    "apps.monitoring",
    "apps.energy",  # اضافه شد
]

# -----------------------------------
# Middleware
# -----------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # برای استاتیک روی Render
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # برای CORS
    "django.middleware.common.CommonMiddleware",
>>>>>>> 894b689 (آخرین تغییرات پروژه (رفع مشکلات Pillow، تنظیمات Render و ...))
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

<<<<<<< HEAD
# ------------------------------
# URL / WSGI / ASGI
# ------------------------------
=======
# -----------------------------------
# URL and WSGI/ASGI
# -----------------------------------
>>>>>>> 894b689 (آخرین تغییرات پروژه (رفع مشکلات Pillow، تنظیمات Render و ...))
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

<<<<<<< HEAD
# ------------------------------
# دیتابیس (SQLite ساده)
# ------------------------------
=======
# -----------------------------------
# Database (SQLite ساده برای Render رایگان)
# -----------------------------------
>>>>>>> 894b689 (آخرین تغییرات پروژه (رفع مشکلات Pillow، تنظیمات Render و ...))
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

<<<<<<< HEAD
# ------------------------------
# Password validation
# ------------------------------
=======
# -----------------------------------
# Templates
# -----------------------------------
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

# -----------------------------------
# Password validation
# -----------------------------------
>>>>>>> 894b689 (آخرین تغییرات پروژه (رفع مشکلات Pillow، تنظیمات Render و ...))
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

<<<<<<< HEAD
# ------------------------------
# بین المللی / زمان
# ------------------------------
=======
# -----------------------------------
# Internationalization
# -----------------------------------
>>>>>>> 894b689 (آخرین تغییرات پروژه (رفع مشکلات Pillow، تنظیمات Render و ...))
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

<<<<<<< HEAD
# ------------------------------
# استاتیک و رسانه
# ------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise برای سرو فایل‌های استاتیک
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------------
# CORS
# ------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ------------------------------
# Django REST Framework
# ------------------------------
=======
# -----------------------------------
# Static files (CSS, JS, Images)
# -----------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -----------------------------------
# Media files
# -----------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------------
# CORS
# -----------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# -----------------------------------
# Default primary key
# -----------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------
# REST Framework
# -----------------------------------
>>>>>>> 894b689 (آخرین تغییرات پروژه (رفع مشکلات Pillow، تنظیمات Render و ...))
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ]
}
<<<<<<< HEAD
=======

# -----------------------------------
# Email (اختیاری، برای ارسال ایمیل)
# -----------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
>>>>>>> 894b689 (آخرین تغییرات پروژه (رفع مشکلات Pillow، تنظیمات Render و ...))
