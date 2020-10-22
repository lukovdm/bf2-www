#!/bin/sh

set -e

echo "Waiting for postgres at host ${DATABASE_HOST}"
until pg_isready --host="${DATABASE_HOST}" --port="${DATABASE_PORT}" --username="${POSTGRES_USER}" --quiet; do
    sleep 1;
done

echo "Postgres database is up"

. .venv/bin/activate

echo "Performing migrations"
./manage.py migrate --no-input

#echo "Collecting static files"
./manage.py collectstatic --no-input

chown --recursive www-data:www-data /bf2-www/

echo "Starting server"
gunicorn --bind :8000 website.wsgi:application