#!/bin/bash

set -e

echo "Starting deployment..."

echo "Checking if DB container is running..."
docker ps | grep medai-db >/dev/null 2>&1 || {
  echo "DB container is not running. Starting it..."
  docker compose up -d db
}

echo "Waiting for Postgres to be ready..."
until docker exec medai-db pg_isready -U postgres > /dev/null 2>&1; do
  sleep 1
done

echo "Database is ready"

echo "Running Alembic migrations..."
alembic upgrade head

echo "Migrations complete"
