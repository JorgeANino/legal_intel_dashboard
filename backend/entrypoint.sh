#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Fix permissions for transformers cache directory
if [ -d "/home/appuser/.cache" ]; then
    echo "Fixing cache directory permissions..."
    chown -R 1000:1000 /home/appuser/.cache
    echo "✓ Cache directory permissions fixed"
fi

# Run database migrations
echo "Running database migrations..."
if [ ! -d "/app/alembic/versions" ] || [ -z "$(ls -A /app/alembic/versions)" ]; then
    echo "No migrations found. Creating initial migration..."
    alembic revision --autogenerate -m "Initial migration"
fi
alembic upgrade head
echo "✓ Database migrations completed"

# Create test user for development
echo "Setting up test user..."
python3 scripts/create_test_user.py
echo "✓ Test user setup completed"

# Start the FastAPI server with hot reload
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
