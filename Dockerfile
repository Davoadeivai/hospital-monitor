FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# نصب وابستگی‌های سیستمی
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# collectstatic
RUN python manage.py collectstatic --noinput

# اجرای migrate + اجرای gunicorn با PORT داینامیک
CMD python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
