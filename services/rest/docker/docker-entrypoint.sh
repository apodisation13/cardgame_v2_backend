#!/bin/bash
# docker-entrypoint.sh
set -e

cd services/rest/app

# Собираем статику
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Применяем миграции
echo "Applying database migrations..."
python manage.py migrate

# Создаем суперпользователя (если переменные окружения заданы)
echo "Creating superuser..."
python manage.py createsuperuser \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "$DJANGO_SUPERUSER_EMAIL" \
    --noinput || true

# Запускаем Gunicorn
echo "Starting Gunicorn..."
exec gunicorn settings.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    "$@"
