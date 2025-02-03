#!/bin/sh
set -e  # Para o script caso algum comando falhe

# Espera o banco de dados ficar pronto antes de rodar qualquer comando
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "🟡 Waiting for Postgres Database Startup ($POSTGRES_HOST $POSTGRES_PORT) ..."
  sleep 2
done

echo "✅ Postgres Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)"

# Se um argumento for passado, executa esse comando
if [ "$#" -gt 0 ]; then
    echo "▶ Running command: $@"
    exec "$@"
else
    echo "⚠ No command provided. Exiting."
    exit 1
fi
