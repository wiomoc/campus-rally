#!/bin/bash
export PYTHONUNBUFFERED=TRUE
python manage.py migrate
exec uvicorn --host 0.0.0.0 --port 8080 asgi:application