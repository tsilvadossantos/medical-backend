#!/bin/bash
# Start all services

set -e

cd "$(dirname "$0")/.."

echo "Starting Medical Backend services..."

# Copy .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

# Load .env to check OLLAMA_URL
source .env 2>/dev/null || true

# Determine if using bundled Ollama
if [ -z "$OLLAMA_URL" ] || [ "$OLLAMA_URL" = "http://ollama:11434" ]; then
    docker-compose -f docker-compose.yml -f docker-compose.ollama.yml up -d --build
else
    docker-compose up -d --build
fi

echo ""
echo "Services started!"
echo "  API:     http://localhost:8000"
echo "  Docs:    http://localhost:8000/docs"
echo ""
echo "First time? Run: ./scripts/init.sh"
