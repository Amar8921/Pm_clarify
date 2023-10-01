#!/bin/sh

echo "Waiting a bit before running migrations..."
sleep 10  # Adjust the sleep duration if needed

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Starting the application..."
exec "$@"
exec gunicorn pmclarify.wsgi:application --bind 0.0.0.0:8000
