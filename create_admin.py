import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    username = "admin"
    password = "admin123"  # حتماً این پسورد را بعد از ورود تغییر دهید!
    
    # حذف یوزر قبلی برای جلوگیری از تداخل
    if User.objects.filter(username=username).exists():
        User.objects.filter(username=username).delete()

    # ساخت سوپریوزر با ایمیل نمایشی
    User.objects.create_superuser(
        username=username, 
        email="admin@internal.local", # یک ایمیل الکی که نیاز به تایید ندارد
        password=password
    )
    
    print("*****************************************")
    print(f"SUCCESS: User '{username}' created!")
    print("*****************************************")

if __name__ == "__main__":
    create_superuser()