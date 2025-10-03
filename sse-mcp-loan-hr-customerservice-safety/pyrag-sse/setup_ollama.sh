#!/bin/bash

# Script to initialize Ollama with required models
echo "Setting up Ollama with embedding models..."

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1
do
    echo -n "."
    sleep 2
done
echo " Ready!"

# Pull required embedding models
echo "Pulling nomic-embed-text model (768 dimensions)..."
docker exec pyrag-ollama ollama pull nomic-embed-text

echo "Checking installed models..."
docker exec pyrag-ollama ollama list

echo "Ollama setup complete!"
