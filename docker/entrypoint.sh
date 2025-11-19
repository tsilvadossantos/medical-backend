#!/bin/bash
set -e

# Database health is handled by docker-compose depends_on condition
# Just start the application
exec "$@"
