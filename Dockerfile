# Use slim Python 3.11 image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files (no Celery now)
RUN python manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Command to run the app with Gunicorn (ASGI if you want Daphne, می‌تونیم تغییر بدیم)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
