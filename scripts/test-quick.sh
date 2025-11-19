#!/bin/bash
# Run tests without coverage (faster)

echo "Running tests..."

if [ -f /.dockerenv ]; then
    pytest app/tests/ -v
else
    if docker-compose ps | grep -q "app.*Up"; then
        docker-compose exec app pytest app/tests/ -v
    else
        pytest app/tests/ -v
    fi
fi
