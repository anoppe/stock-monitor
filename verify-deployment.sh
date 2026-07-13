#!/bin/bash
# Production Deployment Verification Script
# Run this on your server after cloning the repository to verify everything is ready

set -e

echo "========================================="
echo "Stock Monitor - Deployment Verification"
echo "========================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✓ Docker is installed: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi
echo "✓ Docker Compose is installed: $(docker-compose --version)"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo "   Run: cp .env.template .env"
    echo "   Then edit .env with your InfluxDB credentials"
    exit 1
fi
echo "✓ .env file exists"

# Check required environment variables
source .env

if [ "$INFLUXDB_TOKEN" = "YOUR_INFLUXDB_TOKEN_HERE" ]; then
    echo "❌ INFLUXDB_TOKEN not configured in .env"
    echo "   Edit .env and set your actual InfluxDB token"
    exit 1
fi
echo "✓ INFLUXDB_TOKEN is configured"

if [ "$INFLUXDB_ORG" = "YOUR_ORG_NAME_HERE" ]; then
    echo "❌ INFLUXDB_ORG not configured in .env"
    echo "   Edit .env and set your organization name"
    exit 1
fi
echo "✓ INFLUXDB_ORG is configured"

if [ "$INFLUXDB_BUCKET" = "YOUR_BUCKET_NAME_HERE" ]; then
    echo "❌ INFLUXDB_BUCKET not configured in .env"
    echo "   Edit .env and set your bucket name"
    exit 1
fi
echo "✓ INFLUXDB_BUCKET is configured"

echo ""
echo "========================================="
echo "✓ All checks passed!"
echo "========================================="
echo ""
echo "Ready to deploy. Run:"
echo "  docker-compose build"
echo "  docker-compose up -d"
echo ""
echo "After starting, import historical data:"
echo "  docker-compose exec stock-monitor python3 /app/scripts/backfill.py"
echo ""
