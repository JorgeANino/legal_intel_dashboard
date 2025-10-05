#!/bin/bash

# Legal Intel Dashboard - Docker Container Runner
# Usage: ./run_containers.sh [dev|prod]

ENVIRONMENT="${1:-dev}"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|prod)$ ]]; then
    echo "❌ Error: Invalid environment '$ENVIRONMENT'"
    echo "Usage: $0 [dev|prod]"
    echo ""
    echo "Examples:"
    echo "  $0           # Runs in dev mode (default)"
    echo "  $0 dev       # Runs in dev mode"
    echo "  $0 prod      # Runs in production mode"
    exit 1
fi

# Set compose file
if [ "$ENVIRONMENT" = "prod" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV_FILE=".env.prod"
else
    COMPOSE_FILE="docker-compose.yml"
    ENV_FILE=".env"
fi

echo "Legal Intel Dashboard - Docker Setup"
echo "========================================"
echo "Environment: $ENVIRONMENT"
echo "Compose file: $COMPOSE_FILE"
echo ""

# Check if env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  Warning: $ENV_FILE not found"
    if [ -f "${ENV_FILE}.example" ]; then
        echo "Creating $ENV_FILE from ${ENV_FILE}.example"
        cp "${ENV_FILE}.example" "$ENV_FILE"
        echo "✅ $ENV_FILE created. Please update with your actual values."
        echo ""
    else
        echo "❌ Error: ${ENV_FILE}.example not found"
        exit 1
    fi
fi

# Make entrypoint scripts executable
echo "📝 Making entrypoint scripts executable..."
chmod +x backend/entrypoint.sh 2>/dev/null
chmod +x backend/entrypoint.prod.sh 2>/dev/null
chmod +x backend/entrypoint-celery.sh 2>/dev/null

echo "🛑 Stopping existing containers..."
docker-compose -f $COMPOSE_FILE down

echo "Stopping all running Docker containers..."
docker stop $(docker ps -q)

echo "Removing all Docker containers..."
docker rm -f $(docker ps -aq)

echo "Removing all Docker images..."
docker rmi -f $(docker images -aq)

echo "Removing all Docker volumes..."
docker volume rm -f $(docker volume ls -q)

echo "Removing all Docker networks..."
docker network rm $(docker network ls -q) 2>/dev/null

echo "Pruning Docker system (includes containers, networks, images, and build cache)..."
docker system prune -a --volumes -f

echo "Clearing Docker builder cache..."
docker builder prune --all --force

# Build images
echo ""
echo "🔨 Building Docker images..."
docker-compose -f $COMPOSE_FILE build

# Start containers
echo ""
echo "▶️  Starting containers..."
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
echo "===================="
docker-compose -f $COMPOSE_FILE ps

echo ""
echo "✅ Legal Intel Dashboard is running!"
echo ""
echo "📍 Access the application:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/api/v1/docs"
echo "   Flower:    http://localhost:5555 (Celery monitoring)"
echo ""
echo "📝 Useful commands:"
echo "   View logs:     docker-compose -f $COMPOSE_FILE logs -f"
echo "   Stop:          docker-compose -f $COMPOSE_FILE down"
echo "   Restart:       docker-compose -f $COMPOSE_FILE restart"
echo "   Shell:         docker-compose -f $COMPOSE_FILE exec backend bash"
echo ""
