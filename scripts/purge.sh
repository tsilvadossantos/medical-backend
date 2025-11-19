#!/bin/bash
# Stop services and remove all data (volumes)

echo "WARNING: This will delete all data including:"
echo "  - Database contents"
echo "  - Redis data"
echo "  - Ollama models"
echo ""
read -p "Are you sure? (y/N) " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    echo "Purging all services and data..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    echo "All data purged."
else
    echo "Cancelled."
fi
