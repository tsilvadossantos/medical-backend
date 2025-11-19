#!/bin/bash
# Open shell in app container

SERVICE=${1:-"app"}

echo "Opening shell in $SERVICE container..."
docker-compose exec "$SERVICE" /bin/sh
