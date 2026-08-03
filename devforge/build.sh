#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py makemigrations accounts projects assets marketplace workspace notifications messaging
python manage.py migrate
