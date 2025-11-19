#!/bin/bash
# Run tests with coverage

set -e

echo "Running tests with coverage..."

# Check if running in Docker or locally
if [ -f /.dockerenv ]; then
    pytest app/tests/ -v --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=80
else
    # Try to run in container first, fallback to local
    if docker-compose ps | grep -q "app.*Up"; then
        docker-compose exec app pytest app/tests/ -v --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=80
    else
        echo "Running tests locally..."
        pytest app/tests/ -v --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=80
    fi
fi

echo ""
echo "Coverage report generated in htmlcov/index.html"
