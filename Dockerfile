# استفاده از python:3.11-slim (سبک و امن)
FROM python:3.11-slim

# جلوگیری از تولید .pyc و فعال کردن خروجی بدون بافر
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# دایرکتوری کاری
WORKDIR /app

# نصب وابستگی‌های سیستم (فقط چیزهای لازم)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ارتقا pip
RUN pip install --upgrade pip

# کپی requirements و نصب پکیج‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کل پروژه
COPY . .

# جمع‌آوری فایل‌های استاتیک (با --clear برای پاک کردن قدیمی‌ها)
RUN python manage.py collectstatic --noinput --clear

# پورت 8000 را expose کن
EXPOSE 8000

# اجرای برنامه با Gunicorn (برای WSGI)
# اگر از Channels استفاده می‌کنی، می‌توانی به Daphne تغییر دهی
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application", "--workers", "3", "--timeout", "120"]