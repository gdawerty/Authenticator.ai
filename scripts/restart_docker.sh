#!/bin/bash
# Docker Restart Helper Script
# This script attempts to restart Docker using various methods

echo "=========================================="
echo "🐳 DOCKER RESTART HELPER"
echo "=========================================="
echo ""

cd /Users/prathamsaurabh/Authenticator.ai || exit 1

# Try different docker-compose paths
DOCKER_COMPOSE_PATHS=(
    "docker-compose"
    "/usr/local/bin/docker-compose"
    "/opt/homebrew/bin/docker-compose"
    "$(which docker-compose 2>/dev/null)"
    "$(brew --prefix docker-compose)/bin/docker-compose 2>/dev/null"
)

echo "🔍 Looking for docker-compose..."
FOUND_PATH=""
for path in "${DOCKER_COMPOSE_PATHS[@]}"; do
    if [ -n "$path" ] && command -v "$path" &> /dev/null; then
        echo "✅ Found: $path"
        FOUND_PATH="$path"
        break
    fi
done

if [ -z "$FOUND_PATH" ]; then
    echo "❌ docker-compose not found in PATH"
    echo ""
    echo "📋 Tried:"
    for path in "${DOCKER_COMPOSE_PATHS[@]}"; do
        echo "   - $path"
    done
    echo ""
    echo "💡 To fix, try:"
    echo "   1. Install Docker Desktop (includes docker-compose)"
    echo "   2. Or run: brew install docker-compose"
    echo ""
    exit 1
fi

echo ""
echo "📦 Restarting Docker containers..."
echo ""

# Bring down
echo "⬇️  Bringing down containers..."
"$FOUND_PATH" down

# Remove previous images to force rebuild
echo "🗑️  Cleaning up images..."
"$FOUND_PATH" image prune -f || true

# Bring up with build
echo "⬆️  Building and starting containers..."
"$FOUND_PATH" up --build -d

# Wait for containers
echo "⏳ Waiting for containers to be ready..."
sleep 30

# Check status
echo ""
echo "📊 Container Status:"
"$FOUND_PATH" ps

# Check backend health
echo ""
echo "🏥 Checking backend health..."
if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
    curl -s http://localhost:8001/api/health | python3 -m json.tool 2>/dev/null || echo "✅ Backend responding to requests"
else
    echo "⏳ Backend still starting up..."
    sleep 10
    if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
        echo "✅ Backend is now healthy"
    else
        echo "⚠️  Backend not yet responding (may still be starting)"
    fi
fi

echo ""
echo "=========================================="
echo "✅ DOCKER RESTART COMPLETE"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo "   1. Check logs: docker-compose logs backend"
echo "   2. Test classification with sample documents"
echo "   3. Verify Groq fallback is working"
echo "   4. Proceed with frontend integration"
echo ""
