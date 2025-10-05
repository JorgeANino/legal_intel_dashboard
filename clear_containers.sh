#!/bin/bash

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

echo "Restarting Docker service..."
sudo systemctl restart docker

echo "Docker cleanup completed. Everything has been removed."
