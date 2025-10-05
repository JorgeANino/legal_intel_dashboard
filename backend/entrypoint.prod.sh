#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Run database migrations
echo "Running database migrations..."
if [ ! -d "/app/alembic/versions" ] || [ -z "$(ls -A /app/alembic/versions)" ]; then
    echo "No migrations found. Creating initial migration..."
    alembic revision --autogenerate -m "Initial migration"
fi
alembic upgrade head
echo "✓ Database migrations completed"

# Create test user if CREATE_TEST_USER env var is set
if [ "$CREATE_TEST_USER" = "true" ]; then
    echo "Setting up test user..."
    python3 scripts/create_test_user.py
    echo "✓ Test user setup completed"
fi

# Start FastAPI with uvicorn (production mode)
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --timeout-keep-alive 120 \
  --log-level info \
  --proxy-headers \
  --forwarded-allow-ips='*'
