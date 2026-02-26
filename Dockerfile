# استفاده از python:3.11-slim (سبک و امن)
FROM python:3.11-slim

# جلوگیری از تولید .pyc و فعال کردن خروجی بدون بافر
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# دایرکتوری کاری
WORKDIR /app

# نصب وابستگی‌های سیستم (به همراه پکیج‌های مورد نیاز برای psycopg2 و ابزارهای مانیتورینگ)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
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

# اجرای دستورات نهایی با Daphne (چون پروژه شما Channels دارد)
# ۱. انجام Migration برای آپدیت دیتابیس Postgres رندر
# ۲. اجرای سرور روی پورت اختصاصی رندر

CMD sh -c "python manage.py migrate && python create_admin.py && daphne -b 0.0.0.0 -p ${PORT:-8000} config.asgi:application"