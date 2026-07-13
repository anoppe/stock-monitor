# Stock Monitor - Quick Start Guide

## What You Got

A complete Docker-based solution to monitor your BrandNewDay fund:
- Fetches daily NAV data from API
- Stores in InfluxDB
- Visualize in Grafana
- Runs automatically at 12:00 PM CET

## Files Created

```
stock-monitor/
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Portainer deployment config
├── .env.template              # Configuration template (COPY THIS!)
├── .gitignore                 # Git ignore rules
├── README.md                  # Full documentation
├── logs/                      # Log output directory
└── scripts/
    ├── backfill.py           # Import historical data (run once)
    ├── daily_update.py       # Fetch latest data point
    └── scheduler.py          # Main loop (runs daily at 12:00)
```

## Next Steps

### 1. Configure

```bash
cd stock-monitor
cp .env.template .env
nano .env  # Edit with your InfluxDB details
```

**Required values in `.env`:**
- `INFLUXDB_URL` - Your InfluxDB server (e.g., `http://influxdb:8086`)
- `INFLUXDB_TOKEN` - Generate in InfluxDB UI → Data → API Tokens
- `INFLUXDB_ORG` - Your organization name in InfluxDB
- `INFLUXDB_BUCKET` - Create a bucket called `stocks` in InfluxDB
- `UNITS_HELD` - Your actual units (currently 12.0)

### 2. Deploy in Portainer

**Option A: Upload Stack**
1. Open Portainer
2. Go to **Stacks** → **Add Stack**
3. Upload `docker-compose.yml`
4. Paste `.env` content in **Environment Variables**
5. Deploy

**Option B: Command Line**
```bash
docker-compose up -d
docker-compose logs -f
```

### 3. Import Historical Data (One-Time)

After container is running:

```bash
# Via Portainer Console:
python3 /app/scripts/backfill.py

# Or via command line:
docker-compose exec stock-monitor python3 /app/scripts/backfill.py
```

This imports ~3 years of data (2023-05-22 to present).

### 4. Verify in InfluxDB

Open InfluxDB → Data Explorer → Query:

```flux
from(bucket: "stocks")
  |> range(start: -1y)
  |> filter(fn: (r) => r._measurement == "fund_performance")
```

You should see data points.

### 5. Create Grafana Dashboard

1. **Add InfluxDB Data Source** in Grafana
   - URL: `http://influxdb:8086`
   - Query Language: Flux
   - Organization: (from .env)
   - Token: (from .env)
   - Default Bucket: `stocks`

2. **Create Dashboard** with panels:
   - Portfolio value over time
   - NAV (price per unit) over time
   - Daily/weekly change %
   - Year-to-date performance

Sample queries are in the README.md.

## How It Works

1. **Scheduler runs continuously** in Docker container
2. **Every day at 12:00 PM CET**, it:
   - Fetches latest NAV from API
   - Calculates portfolio value (NAV × units)
   - Writes to InfluxDB
3. **Grafana queries InfluxDB** to display charts

## Monitoring

```bash
# Check if scheduler is running
docker-compose logs stock-monitor | grep "Next run scheduled"

# View all logs
docker-compose logs -f

# Restart if needed
docker-compose restart
```

## Troubleshooting

**Container won't start?**
- Check `.env` has all required values
- Verify InfluxDB URL is reachable

**No data in InfluxDB?**
- Run backfill script manually
- Check InfluxDB token has write permissions
- Verify bucket name matches `.env`

**Scheduler not running?**
- Check container logs: `docker-compose logs`
- Ensure timezone is correct in `.env`

## Next: Grafana Dashboard Ideas

- **Line chart**: Portfolio value over time
- **Stat panel**: Current value, 24h change %
- **Line chart**: NAV price history
- **Stat panel**: Total gain/loss (vs start value)
- **Table**: Recent transactions (if you add buy/sell tracking)

Full documentation in README.md.

---

**Questions?** Check the README or inspect the Python scripts - they're well commented!
