#!/bin/sh

echo "Waiting a bit before running migrations..."
sleep 200  # Adjust the sleep duration if needed

echo "Running migrations..."
python manage.py migrate
python manage.py populate_data

echo "Starting the application..."
exec "$@"
exec gunicorn pmclarify.wsgi:application --bind 0.0.0.0:8000
