#!/bin/bash
# Docker build and run script

echo "Building and starting MSSQL MCP SSE Server with Docker..."

# Copy .env.example to .env if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

# Build and start containers
docker compose build --no-cache
docker compose up
