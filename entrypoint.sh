#!/bin/sh
set -e

echo "Running entrypoint script..."

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting application..."
exec "$@"
