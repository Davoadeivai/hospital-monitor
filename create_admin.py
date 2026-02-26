import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    # گرفتن اطلاعات از پنل Render
    username = os.environ.get("ADMIN_USERNAME", "admin_hospital")
    password = os.environ.get("ADMIN_PASSWORD", "Pass12345678")
    email = "admin@example.com"

    # حذف هرگونه یوزر قبلی با این نام برای اطمینان از تازگی پسورد
    if User.objects.filter(username=username).exists():
        User.objects.filter(username=username).delete()
        print(f"--- Old user '{username}' deleted ---")

    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"--- Superuser '{username}' created with password: {password} ---")

if __name__ == "__main__":
    try:
        create_superuser()
    except Exception as e:
        print(f"--- Error creating superuser: {e} ---")