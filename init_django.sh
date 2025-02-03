#!/bin/bash

export PATH=/opt/condaenv/bin:$PATH

python manage.py makemigrations base
python manage.py migrate --fake-initial --noinput
python manage.py migrate --fake contenttypes
python manage.py collectstatic --noinput
python manage.py createsuperuser \
    --noinput \
    --username freva-admin \
    --email $DJANGO_SUPERUSER_EMAIL || echo 0
python manage.py shell -c \
    'from django.contrib.sites.models import Site; Site.objects.create(id=1, domain="example.com", name="example.com").save()' || echo 0
gunicorn -b [::]:8000 --timeout 900 -w 1 django_evaluation.wsgi
