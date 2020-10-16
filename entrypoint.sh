#!/bin/sh

set -e

. .venv/bin/activate

./manage.py migrate --no-input

chown --recursive www-data:www-data /bf2-www/

./manage.py runserver 0.0.0.0:8000