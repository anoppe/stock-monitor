#!/bin/bash
# Quick start script for the test environment

set -e

echo "========================================="
echo "Stock Monitor - Test Environment Startup"
echo "========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Start services
echo "Starting services..."
docker-compose -f docker-compose.test.yml up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "Service Status:"
docker-compose -f docker-compose.test.yml ps

echo ""
echo "========================================="
echo "✓ Test Environment Started!"
echo "========================================="
echo ""
echo "Access your services:"
echo "  📊 Grafana:  http://localhost:3000"
echo "     Login:    admin / admin"
echo ""
echo "  💾 InfluxDB: http://localhost:8086"
echo "     Login:    admin / adminpassword123"
echo ""
echo "Next steps:"
echo "  1. Import historical data:"
echo "     docker-compose -f docker-compose.test.yml exec stock-monitor python3 /app/scripts/backfill.py"
echo ""
echo "  2. View logs:"
echo "     docker-compose -f docker-compose.test.yml logs -f"
echo ""
echo "  3. Open Grafana dashboard:"
echo "     open http://localhost:3000"
echo ""
echo "For more information, see README.TEST.md"
echo "========================================="
