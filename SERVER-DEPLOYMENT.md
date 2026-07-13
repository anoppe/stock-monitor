# Server Deployment Instructions

Quick guide for deploying Stock Monitor on your production server.

## 📦 On Your Server

### 1. Clone the Repository

```bash
git clone https://github.com/anoppe/stock-monitor.git
cd stock-monitor
```

### 2. Verify Prerequisites

```bash
./verify-deployment.sh
```

This will check:
- Docker is installed
- Docker Compose is installed
- .env file exists and is configured

### 3. Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit with your credentials
nano .env
```

**Required settings:**
```bash
INFLUXDB_URL=http://your-influxdb:8086
INFLUXDB_TOKEN=your_actual_token
INFLUXDB_ORG=your_org_name
INFLUXDB_BUCKET=stocks
UNITS_HELD=12.0
```

### 4. Build and Deploy

```bash
# Build the Docker image
docker-compose build

# Start the container
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 5. Import Historical Data

```bash
# Run once to import ~3 years of data
docker-compose exec stock-monitor python3 /app/scripts/backfill.py
```

## ✅ Verification

### Check Container Status

```bash
docker-compose ps
```

Expected output:
```
NAME              IMAGE             STATUS
stock-monitor     stock-monitor     Up X minutes (healthy)
```

### View Logs

```bash
# Should show scheduler running
docker-compose logs stock-monitor | grep "Next run scheduled"
```

### Test InfluxDB Connection

```bash
docker-compose exec stock-monitor python3 -c "
from influxdb_client import InfluxDBClient
import os
client = InfluxDBClient(
    url=os.getenv('INFLUXDB_URL'),
    token=os.getenv('INFLUXDB_TOKEN'),
    org=os.getenv('INFLUXDB_ORG')
)
print('✓ InfluxDB connection OK' if client.ping() else '✗ Connection failed')
client.close()
"
```

## 🔄 Daily Operations

The container runs continuously and updates data daily at 12:00 PM CET.

**View next scheduled run:**
```bash
docker-compose logs stock-monitor | tail -20
```

**Manual update:**
```bash
docker-compose exec stock-monitor python3 /app/scripts/daily_update.py
```

**Restart:**
```bash
docker-compose restart
```

**Stop:**
```bash
docker-compose down
```

## 📊 Connect Grafana

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete Grafana setup instructions.

Quick steps:
1. Add InfluxDB data source in Grafana
2. Import `grafana-provisioning/dashboards/stock-monitor-dashboard.json`
3. View your portfolio data!

## 🐛 Troubleshooting

**Container won't start:**
```bash
docker-compose logs
```

**No data in InfluxDB:**
- Verify InfluxDB token has read/write permissions
- Check bucket name matches .env
- Run backfill script

**Need help?**
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting
- Review logs: `docker-compose logs -f`

---

For complete documentation, see:
- [README.md](README.md) - Full project documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
- [README.TEST.md](README.TEST.md) - Local testing with included test environment
