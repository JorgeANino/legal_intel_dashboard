#!/bin/sh

# Wait for postgres
if [ "$DATABASE" = "postgres" ] || [ -n "$POSTGRES_HOST" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 0.1
done
echo "Redis started"

# Fix permissions for transformers cache directory
if [ -d "/home/appuser/.cache" ]; then
    echo "Fixing cache directory permissions..."
    chown -R 1000:1000 /home/appuser/.cache
    echo "✓ Cache directory permissions fixed"
fi

echo "Starting Celery worker..."

# Start Celery worker
exec celery -A app.core.celery_app worker --loglevel=info --concurrency=2
