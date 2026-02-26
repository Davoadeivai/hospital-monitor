import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    # این مقادیر را از پنل Render که دقایقی پیش تنظیم کردیم می‌خواند
    username = os.environ.get("ADMIN_USERNAME", "admin")
    password = os.environ.get("ADMIN_PASSWORD", "admin123456")
    email = "admin@example.com"

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"--- Superuser '{username}' created! ---")
    else:
        print(f"--- Superuser '{username}' already exists. ---")

if __name__ == "__main__":
    create_superuser()