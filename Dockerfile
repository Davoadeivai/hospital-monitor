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
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ارتقا pip
RUN pip install --upgrade pip

# کپی requirements و نصب پکیج‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کل پروژه
COPY . .

# جمع‌آوری فایل‌های استاتیک
RUN python manage.py collectstatic --noinput --clear

# رندر از پورت داینامیک استفاده می‌کند، پس EXPOSE ثابت را حذف می‌کنیم

# دستور اجرای نهایی:
# ۱. ابتدا دیتابیس را آپدیت می‌کند
# ۲. سپس سرور را روی پورتی که رندر اختصاص داده اجرا می‌کند
CMD sh -c "python manage.py migrate && gunicorn --bind 0.0.0.0:${PORT:-8000} config.wsgi:application --workers 3 --timeout 120"