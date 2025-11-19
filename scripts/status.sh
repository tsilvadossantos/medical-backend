#!/bin/bash
# Show status of all services

echo "Service Status:"
echo "==============="
docker-compose ps

echo ""
echo "Health Checks:"
echo "=============="

# API health
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "API:     ✓ healthy"
else
    echo "API:     ✗ not responding"
fi

# Database
if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo "DB:      ✓ healthy"
else
    echo "DB:      ✗ not responding"
fi

# Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "Redis:   ✓ healthy"
else
    echo "Redis:   ✗ not responding"
fi

# Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Ollama:  ✓ healthy"
else
    echo "Ollama:  ✗ not responding"
fi
