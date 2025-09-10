#!/bin/bash
set -e

: "${DB_HOST:=db}"
: "${DB_PORT:=5432}"

echo "Waiting for postgres at ${DB_HOST}:${DB_PORT}..."

# wait until the DB port is open
until nc -z ${DB_HOST} ${DB_PORT}; do
  echo "Postgres not ready - sleeping 1s"
  sleep 1
done

echo "Postgres is up - running migrations and collectstatic"

# apply database migrations
python manage.py migrate --noinput

echo "Loading initial Excel data..."
python manage.py shell -c "from creditcardapp.tasks import load_customers, load_loans; load_customers.delay(); load_loans.delay()"

echo "Resetting sequences..."
# Reset all sequences for your app (replace `creditcardapp` with your app name)
python manage.py sqlsequencereset creditcardapp | python manage.py dbshell

# collect static files
python manage.py collectstatic --noinput

exec "$@"


