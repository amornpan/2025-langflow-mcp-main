#!/bin/bash
# Ollama startup script with model pulling

# Start Ollama in the background
/bin/ollama serve &

# Store the PID
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Starting Ollama server..."
sleep 10

# Try to pull the model multiple times
MAX_RETRIES=5
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "Attempt $((RETRY_COUNT + 1)) to pull model..."
    
    if /bin/ollama pull nomic-embed-text; then
        echo "Model pulled successfully!"
        break
    else
        echo "Failed to pull model, retrying in 5 seconds..."
        sleep 5
        RETRY_COUNT=$((RETRY_COUNT + 1))
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "Warning: Could not pull model after $MAX_RETRIES attempts"
    echo "You may need to pull it manually: docker exec pyrag-ollama ollama pull nomic-embed-text"
fi

# Keep Ollama running in foreground
echo "Ollama server is running..."
wait $OLLAMA_PID
