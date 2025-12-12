#!/bin/sh
set -e

echo "Rodando migrations..."
alembic upgrade head

echo "Iniciando aplicação..."
exec "$@"
