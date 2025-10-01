#!/bin/sh
set -e

echo "Running entrypoint script..."

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting application..."
exec "$@"