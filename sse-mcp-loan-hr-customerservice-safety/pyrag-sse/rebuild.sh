#!/bin/bash

# Rebuild and restart Docker containers
echo "Rebuilding PyRAGDoc SSE Server..."

# Stop existing containers
echo "Stopping containers..."
docker-compose down

# Remove old volumes if needed (optional - comment out if you want to keep data)
# echo "Removing old volumes..."
# docker-compose down -v

# Make sure ollama-entrypoint.sh has execute permission
echo "Setting permissions..."
chmod +x ollama-entrypoint.sh

# Build with no cache to ensure fresh build
echo "Building containers..."
docker-compose build --no-cache

# Start services
echo "Starting services..."
docker-compose up
