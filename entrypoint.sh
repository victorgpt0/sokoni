#!/bin/sh
set -e

echo "Running entrypoint script..."

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting Gunicorn..."
exec gunicorn sokoni.wsgi:application --bind=0.0.0.0:8000 --workers=4 --threads=2 --timeout=120 --access-logfile - --error-logfile -