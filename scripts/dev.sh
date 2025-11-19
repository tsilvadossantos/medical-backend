#!/bin/bash
# Start in development mode with live reload

set -e

echo "Starting in development mode..."

# Copy .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

docker-compose up --build

# This runs in foreground for live logs
