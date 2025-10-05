#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Wait for the backend container to finish database setup
echo "Waiting for backend to complete database setup..."
sleep 10

# Fix permissions for transformers cache directory
if [ -d "/home/appuser/.cache" ]; then
    echo "Fixing cache directory permissions..."
    chown -R 1000:1000 /home/appuser/.cache
    echo "✓ Cache directory permissions fixed"
fi

exec "$@"
