#!/bin/bash
# Restart all services

echo "Restarting Medical Backend services..."
docker-compose down
docker-compose up -d --build
echo "Services restarted."
