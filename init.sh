#!/bin/sh

set -e

echo "⏳ Waiting for PostgreSQL and Redis..."
./wait-for-it.sh -t 60 db:5433
./wait-for-it.sh -t 60 redis:6379

echo "Database is ready."

python manage.py migrate --noinput
python manage.py create_default_superuser

python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4