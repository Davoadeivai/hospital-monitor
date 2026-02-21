FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput --ignore="*.map" || true

ENV DJANGO_SETTINGS_MODULE=config.render_settings
ENV PORT=8000

RUN python manage.py migrate --run-syncdb || true

RUN python manage.py shell -c "\
from django.contrib.auth.models import User; \
User.objects.filter(username='admin').exists() or \
User.objects.create_superuser('admin','admin@hospital.ir','admin123')" || true

EXPOSE 8000

CMD daphne -b 0.0.0.0 -p $PORT config.asgi:application
