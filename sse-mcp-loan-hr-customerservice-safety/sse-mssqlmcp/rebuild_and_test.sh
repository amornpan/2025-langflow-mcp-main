#!/bin/bash
# Complete rebuild and test script for MSSQL MCP SSE Server

echo "==================================="
echo "🧹 Cleaning up old containers..."
echo "==================================="

# Stop and remove containers
docker compose down

# Remove old images
docker rmi mssql-mcp-sse:latest 2>/dev/null || true
docker rmi sse-mssqlmcp-mcp-server:latest 2>/dev/null || true

# Clean up volumes and networks
docker volume prune -f
docker network prune -f

echo ""
echo "==================================="
echo "🔨 Building new container..."
echo "==================================="

# Build new image
docker compose build --no-cache

echo ""
echo "==================================="
echo "🚀 Starting server..."
echo "==================================="

# Start in detached mode
docker compose up -d

# Wait for server to be ready
echo ""
echo "⏳ Waiting for server to be ready..."
sleep 5

# Check health
echo ""
echo "==================================="
echo "🏥 Checking server health..."
echo "==================================="

health_check() {
    curl -s -f http://localhost:9000/health > /dev/null 2>&1
}

max_attempts=10
attempt=1

while [ $attempt -le $max_attempts ]; do
    if health_check; then
        echo "✅ Server is healthy!"
        break
    else
        echo "⏳ Waiting for server... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Server failed to start!"
    echo "📋 Showing logs:"
    docker compose logs
    exit 1
fi

# Show server info
echo ""
echo "==================================="
echo "📊 Server Information"
echo "==================================="
curl -s http://localhost:9000/ | python3 -m json.tool

# Run tests
echo ""
echo "==================================="
echo "🧪 Running tests..."
echo "==================================="

# Check if test client exists
if [ -f "test_client.py" ]; then
    # Create virtual environment if not exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate and install dependencies
    source venv/bin/activate
    pip install -q httpx mcp
    
    # Run test
    python test_client.py
    test_result=$?
    
    deactivate
    
    if [ $test_result -eq 0 ]; then
        echo ""
        echo "✅ All tests passed!"
    else
        echo ""
        echo "❌ Tests failed!"
    fi
else
    echo "⚠️  test_client.py not found, skipping tests"
fi

# Show logs
echo ""
echo "==================================="
echo "📋 Recent server logs:"
echo "==================================="
docker compose logs --tail=20

echo ""
echo "==================================="
echo "✨ Rebuild complete!"
echo "==================================="
echo "🌐 Server is running at: http://localhost:9000"
echo "📝 View logs: docker compose logs -f"
echo "🛑 Stop server: docker compose down"
echo ""
