#!/bin/bash
# Import historical data into test environment

set -e

echo "========================================="
echo "Stock Monitor - Import Historical Data"
echo "========================================="
echo ""

# Check if services are running
if ! docker-compose -f docker-compose.test.yml ps | grep -q "stock-monitor-app"; then
    echo "❌ Error: Test environment is not running."
    echo "   Start it first with: ./start-test.sh"
    exit 1
fi

echo "Importing historical fund data..."
echo ""

docker-compose -f docker-compose.test.yml exec stock-monitor python3 /app/scripts/backfill.py

echo ""
echo "========================================="
echo "✓ Historical Data Import Complete!"
echo "========================================="
echo ""
echo "View your data:"
echo "  📊 Grafana Dashboard: http://localhost:3000"
echo "  💾 InfluxDB Explorer:  http://localhost:8086"
echo ""
