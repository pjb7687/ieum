#!/bin/bash

while ! nc -z db 5432; do
    sleep 10
done

python manage.py migrate
python manage.py ensure_superuser

if [ "$DEBUG" = "True" ]; then
    python manage.py runserver 0.0.0.0:8080
else
    python -m uvicorn backend.asgi:application --host 0.0.0.0 --port 8080
fi