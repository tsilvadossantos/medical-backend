#!/bin/bash
# Reset database (drop and recreate)

echo "WARNING: This will delete all database data!"
read -p "Are you sure? (y/N) " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    echo "Resetting database..."
    docker-compose exec db psql -U postgres -c "DROP DATABASE IF EXISTS medical_db;"
    docker-compose exec db psql -U postgres -c "CREATE DATABASE medical_db;"

    # Restart app to reinitialize tables
    docker-compose restart app worker

    echo "Database reset complete."
else
    echo "Cancelled."
fi
