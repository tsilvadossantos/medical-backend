#!/bin/bash
# Full automated setup and start - single command to run everything

set -e

echo "=========================================="
echo "  Medical Backend - Full Automated Setup"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

# 1. Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env from .env.example"
else
    echo "✓ .env already exists"
fi

# Load .env to check OLLAMA_URL
source .env 2>/dev/null || true

# Determine if using bundled Ollama
USE_BUNDLED_OLLAMA=false
if [ -z "$OLLAMA_URL" ] || [ "$OLLAMA_URL" = "http://ollama:11434" ]; then
    USE_BUNDLED_OLLAMA=true
fi

# 2. Build and start services
echo ""
echo "Starting services..."

if [ "$USE_BUNDLED_OLLAMA" = true ]; then
    echo "  (with bundled Ollama)"
    docker-compose -f docker-compose.yml -f docker-compose.ollama.yml up -d --build
else
    echo "  (using external Ollama at $OLLAMA_URL)"
    docker-compose up -d --build
fi

# 3. Wait for services to be healthy
echo ""
echo "Waiting for services to be ready..."

# Wait for database
echo -n "  Database: "
until docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; do
    sleep 1
done
echo "✓"

# Wait for Redis
echo -n "  Redis: "
until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    sleep 1
done
echo "✓"

# Wait for Ollama (bundled or external)
if [ "$USE_BUNDLED_OLLAMA" = true ]; then
    echo -n "  Ollama: "
    until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
        sleep 1
    done
    echo "✓"
else
    echo -n "  Ollama (external): "
    OLLAMA_HOST=$(echo "$OLLAMA_URL" | sed 's|http://||' | sed 's|:.*||')
    OLLAMA_PORT=$(echo "$OLLAMA_URL" | sed 's|.*:||' | sed 's|/.*||')
    if curl -s "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
        echo "✓"
    else
        echo "⚠ not responding (will use fallback)"
    fi
fi

# Wait for API
echo -n "  API: "
until curl -s http://localhost:8000/health > /dev/null 2>&1; do
    sleep 1
done
echo "✓"

# 4. Pull Ollama model if using bundled Ollama
if [ "$USE_BUNDLED_OLLAMA" = true ]; then
    echo ""
    echo "Checking Ollama model..."
    MODEL=${OLLAMA_MODEL:-llama3.2}

    if ! docker-compose exec -T ollama ollama list 2>/dev/null | grep -q "$MODEL"; then
        echo "Pulling $MODEL (this may take a few minutes on first run)..."
        docker-compose exec -T ollama ollama pull "$MODEL"
        echo "✓ Model $MODEL ready"
    else
        echo "✓ Model $MODEL already available"
    fi
fi

# 5. Done!
echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "  API:      http://localhost:8000"
echo "  Docs:     http://localhost:8000/docs"
echo "  Health:   http://localhost:8000/health"
echo ""
echo "  Commands:"
echo "    ./scripts/status.sh   - Check service status"
echo "    ./scripts/logs.sh     - View logs"
echo "    ./scripts/test.sh     - Run tests"
echo "    ./scripts/stop.sh     - Stop services"
echo ""
