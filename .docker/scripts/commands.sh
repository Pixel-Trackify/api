#!/bin/sh

# O shell irá encerrar a execução do script quando um comando falhar
set -e

if [ "$APP_AMBIENT" = "development" ]; then
  while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    echo "🟡 Waiting for Postgres Database Startup ($POSTGRES_HOST $POSTGRES_PORT) ..."
    sleep 2
  done
fi

echo "✅ Postgres Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)"

exec uwsgi --http :8000 --module project.wsgi --master --processes 4 --threads 2