#!/usr/bin/env sh
set -eu

/app/scripts/wait-for-db.sh postgres:5432 true
python manage.py validate_s3_config --strict
python manage.py migrate --noinput
python manage.py seed_site
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers "${GUNICORN_WORKERS:-3}"

