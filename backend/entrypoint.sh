#!/bin/sh
set -e

echo "==> Waiting for database..."
# Wait until postgres is accepting connections
until python -c "import dj_database_url, psycopg2; u = dj_database_url.config(); psycopg2.connect(dbname=u['NAME'], user=u['USER'], password=u['PASSWORD'], host=u['HOST'], port=u['PORT'])" 2>/dev/null; do
  sleep 1
done
echo "==> Database is ready."

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Creating default superuser (if not existing)..."
python manage.py createsuperuser --noinput 2>/dev/null || true

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Starting server..."
exec "$@"
