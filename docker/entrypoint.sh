#!/bin/sh

set -o errexit
set -o nounset

python backend/manage.py migrate --noinput
python backend/manage.py collectstatic --noinput

exec gunicorn core.wsgi:application \
    --chdir backend \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout "${GUNICORN_TIMEOUT:-60}"
