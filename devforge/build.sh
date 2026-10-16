#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --run-syncdb

# Ensure the django_site record exists for SITE_ID=1 (required by allauth)
python manage.py shell -c "
from django.contrib.sites.models import Site
Site.objects.update_or_create(
    id=1,
    defaults={'domain': '${RENDER_EXTERNAL_HOSTNAME:-localhost}', 'name': 'DevForge'}
)
print('[BUILD] Site record ensured: id=1')
"

# Create superuser if not exists
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
import os
u = os.environ.get('DJANGO_SUPERUSER_USERNAME', '')
e = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
p = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
if u and e and p and not User.objects.filter(username=u).exists():
    User.objects.create_superuser(u, e, p)
    print(f'[BUILD] Superuser {u} created.')
else:
    print('[BUILD] Superuser already exists or env vars not set.')
"