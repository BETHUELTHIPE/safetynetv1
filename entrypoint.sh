#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Wait for PostgreSQL to be available
postgres_ready() {
    python << END
import sys
import psycopg2
try:
    psycopg2.connect(
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput && python manage.py createcachetable && exec gunicorn cpfcrimereportingsystem.wsgi:application --bind 0.0.0.0:8081 --workers 3 --timeout 120 --log-level=info

# Create superuser if specified in environment
if [ "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    echo "Creating superuser ${DJANGO_SUPERUSER_USERNAME}..."
    python manage.py createsuperuser --noinput || true
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the command passed to the entrypoint
exec "$@"
