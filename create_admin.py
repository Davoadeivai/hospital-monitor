import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    username = os.environ.get("ADMIN_USERNAME", "Davoad")
    password = os.environ.get("ADMIN_PASSWORD", "Dau8nbt37v@")
    email = "admin@example.com"

    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    
    # ست کردن یا آپدیت کردن پسورد در هر شرایطی
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    
    if created:
        print(f"--- User '{username}' created successfully! ---")
    else:
        print(f"--- User '{username}' already existed, password updated! ---")

if __name__ == "__main__":
    create_superuser()