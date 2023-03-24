#!/bin/sh

set -e

. .venv/bin/activate

echo "Performing migrations"
./manage.py migrate --no-input

echo "compiling scss to css"
./manage.py compilescss

echo "Collecting static files"
./manage.py collectstatic --no-input

chown --recursive www-data:www-data /bf2-www/

echo "Starting server"
gunicorn --bind :8080 website.wsgi:application