#!/bin/bash
# Stop all services

cd "$(dirname "$0")/.."

echo "Stopping Medical Backend services..."
docker-compose -f docker-compose.yml -f docker-compose.ollama.yml down 2>/dev/null || docker-compose down
echo "Services stopped."
