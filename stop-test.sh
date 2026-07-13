#!/bin/bash
# Stop and clean up test environment

set -e

echo "========================================="
echo "Stock Monitor - Test Environment Cleanup"
echo "========================================="
echo ""

# Ask for confirmation
read -p "Do you want to delete all data? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping services and removing volumes..."
    docker-compose -f docker-compose.test.yml down -v
    echo ""
    echo "✓ Test environment completely removed (including data)"
else
    echo "Stopping services (keeping data)..."
    docker-compose -f docker-compose.test.yml down
    echo ""
    echo "✓ Test environment stopped (data preserved)"
fi

echo ""
echo "To start again: ./start-test.sh"
echo "========================================="
