# Production Deployment Guide

This guide covers deploying the Stock Monitor application on your production server.

## 🚀 Quick Deployment

### Prerequisites

- Docker and Docker Compose installed on your server
- Access to an InfluxDB instance (v2.x)
- InfluxDB bucket created and API token generated

### Step-by-Step Deployment

#### 1. Clone the Repository

```bash
git clone https://github.com/anoppe/stock-monitor.git
cd stock-monitor
```

#### 2. Configure Environment Variables

Copy the template and edit with your real values:

```bash
cp .env.template .env
nano .env
```

**Required Configuration:**

```bash
# InfluxDB Configuration
INFLUXDB_URL=http://your-influxdb-server:8086
INFLUXDB_TOKEN=your_actual_influxdb_token_here
INFLUXDB_ORG=your_organization_name
INFLUXDB_BUCKET=stocks

# Fund Configuration
FUND_ID=8015
FUND_NAME=BND_Wereld_Indexfonds_Totaal_Carbon_Screened
UNITS_HELD=12.0

# Scheduler Configuration
UPDATE_HOUR=12
UPDATE_MINUTE=0
TIMEZONE=Europe/Amsterdam
```

#### 3. Build and Start the Container

```bash
# Build the image
docker-compose build

# Start the container
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### 4. Import Historical Data (One-Time)

After the container is running, import historical data:

```bash
docker-compose exec stock-monitor python3 /app/scripts/backfill.py
```

This will import approximately 3 years of historical data.

## 📋 Production Architecture

```
┌─────────────────────┐
│  Stock Monitor App  │
│  (Docker Container) │
└──────────┬──────────┘
           │
           ├──> Fund API (External)
           │    https://devrobotapi.azurewebsites.net
           │
           └──> Your InfluxDB Server
                (External or Docker)
```

## 🔧 Configuration Details

### InfluxDB Setup

Before deploying, ensure you have:

1. **Created an InfluxDB bucket** named `stocks` (or any name, update `.env`)
2. **Generated an API token** with read/write access to the bucket
3. **Network access** from the stock-monitor container to InfluxDB

### Scheduler Behavior

- Runs continuously in the container
- Fetches latest data daily at the specified time (default: 12:00 PM)
- Uses timezone-aware scheduling (default: Europe/Amsterdam)
- Logs all operations to stdout and `/app/logs/`

### Network Configuration

The default `docker-compose.yml` runs the container in bridge mode. If your InfluxDB is:

**On the same Docker network:**
```yaml
# Uncomment in docker-compose.yml
networks:
  monitoring:
    external: true
```

**On a different server:**
- Use the full URL in `INFLUXDB_URL`
- Ensure firewall allows outbound connections

## 🔄 Maintenance

### View Logs

```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

### Restart Container

```bash
docker-compose restart
```

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Manual Data Fetch

```bash
# Trigger an immediate data update
docker-compose exec stock-monitor python3 /app/scripts/daily_update.py
```

### Update Units Held

When you buy or sell fund units:

1. Edit `.env` and update `UNITS_HELD`
2. Restart the container: `docker-compose restart`

The next update will use the new unit count. Historical data remains unchanged.

## 📊 Grafana Integration

Connect your Grafana instance to the InfluxDB bucket to visualize the data.

### Add InfluxDB Data Source

1. Go to **Configuration** → **Data Sources** → **Add data source**
2. Select **InfluxDB**
3. Configure:
   - **Query Language**: Flux
   - **URL**: Your InfluxDB URL
   - **Organization**: Your org name
   - **Token**: Your InfluxDB token
   - **Default Bucket**: `stocks`
4. **Save & Test**

### Import Dashboard

A pre-built dashboard is available in `grafana-provisioning/dashboards/stock-monitor-dashboard.json`

**To import:**
1. In Grafana, go to **Dashboards** → **Import**
2. Upload or paste the JSON content
3. Select your InfluxDB data source
4. Import

The dashboard includes:
- Current portfolio value
- Current NAV (unit price)
- 30-day return percentage
- Historical charts (1 year)
- Recent data table

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check environment variables
docker-compose config

# Check logs for errors
docker-compose logs
```

### No Data in InfluxDB

```bash
# Verify InfluxDB connection
docker-compose exec stock-monitor python3 -c "
from influxdb_client import InfluxDBClient
import os
client = InfluxDBClient(
    url=os.getenv('INFLUXDB_URL'),
    token=os.getenv('INFLUXDB_TOKEN'),
    org=os.getenv('INFLUXDB_ORG')
)
print('InfluxDB connection: OK' if client.ping() else 'FAILED')
client.close()
"

# Check InfluxDB token permissions
# Ensure the token has read/write access to the bucket

# Run backfill script
docker-compose exec stock-monitor python3 /app/scripts/backfill.py
```

### Fund API Not Responding

```bash
# Test API manually
curl "https://devrobotapi.azurewebsites.net/v1/fundrates?id=8015" | jq | head -30
```

### Scheduler Not Running

```bash
# Check if process is running
docker-compose exec stock-monitor ps aux | grep scheduler

# View scheduler logs
docker-compose logs stock-monitor | grep "Next run scheduled"
```

## 🔐 Security Best Practices

### Protect Your Secrets

- **Never commit `.env` file** to version control (.gitignore handles this)
- Store sensitive values in environment variables or secrets management
- Use read-only InfluxDB tokens if possible
- Restrict network access to InfluxDB

### Use Docker Secrets (Optional)

For enhanced security in production:

```yaml
# docker-compose.yml
services:
  stock-monitor:
    secrets:
      - influxdb_token
    environment:
      INFLUXDB_TOKEN_FILE: /run/secrets/influxdb_token

secrets:
  influxdb_token:
    external: true
```

## 📦 Backup Strategy

### What to Back Up

1. **InfluxDB data** - Primary data store
2. **`.env` file** - Configuration (store securely)
3. **Application logs** - `/app/logs/` (optional)

### Automated Backups

Set up InfluxDB backups using `influx backup`:

```bash
# Example backup script
influx backup /backup/path \
  --host http://your-influxdb:8086 \
  --token your-token
```

## 🔄 Alternative Deployment Methods

### Portainer

1. Upload `docker-compose.yml` as a stack
2. Add environment variables in Portainer UI
3. Deploy the stack

### Kubernetes

A Helm chart or Kubernetes manifests can be created. Contact for details.

### Standalone Docker

```bash
# Build image
docker build -t stock-monitor .

# Run container
docker run -d \
  --name stock-monitor \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  stock-monitor
```

## 📊 Data Schema Reference

The application writes data to InfluxDB with this structure:

```
Measurement: fund_performance

Tags:
  - fund_id: 8015
  - fund_name: BND_Wereld_Indexfonds_Totaal_Carbon_Screened

Fields:
  - nav (float): Net Asset Value per unit
  - bid_price (float): Bid price
  - ask_price (float): Ask price
  - units_held (float): Number of units owned
  - portfolio_value (float): Total value (nav × units_held)

Timestamp: Date from API
```

## 🆘 Support

For issues or questions:

1. Check the logs: `docker-compose logs -f`
2. Review [README.md](README.md) for detailed documentation
3. Open an issue on GitHub

## 📝 License

MIT License - See LICENSE file for details
