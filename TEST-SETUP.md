# Stock Monitor - Test Environment Setup

## Files Created

```
stock-monitor/
├── docker-compose.test.yml                    # Complete test stack (InfluxDB + Grafana + App)
├── README.TEST.md                             # Test environment documentation
├── start-test.sh                              # Quick start script
├── import-data.sh                             # Import historical data script
├── stop-test.sh                               # Cleanup script
└── grafana-provisioning/
    ├── datasources/
    │   └── influxdb.yml                      # Auto-configured InfluxDB datasource
    └── dashboards/
        ├── dashboard-provider.yml            # Dashboard auto-loader config
        └── stock-monitor-dashboard.json      # Pre-built Grafana dashboard
```

## Quick Start Commands

### Start Everything
```bash
./start-test.sh
```

This will:
- Start InfluxDB, Grafana, and Stock Monitor containers
- Auto-configure InfluxDB with bucket and token
- Auto-provision Grafana datasource and dashboard
- Display access URLs and credentials

### Import Historical Data
```bash
./import-data.sh
```

Imports ~3 years of historical fund data (2023-05-22 to present).

### Stop Everything
```bash
./stop-test.sh
```

Prompts whether to keep or delete data.

## Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin / admin |
| InfluxDB | http://localhost:8086 | admin / adminpassword123 |

## Test Credentials

**⚠️ These are test-only credentials - DO NOT use in production!**

```bash
# InfluxDB
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=test-token-stock-monitor-12345
INFLUXDB_ORG=stock-monitor
INFLUXDB_BUCKET=stocks

# Grafana
Username: admin
Password: admin
```

## Dashboard Features

The auto-provisioned Grafana dashboard includes:

1. **Stats Panels**
   - Current Portfolio Value
   - Current NAV (Unit Price)
   - 30-Day Return %
   - Units Held

2. **Time Series Charts**
   - Portfolio Value Over Time (1 Year)
   - NAV Price Over Time (1 Year)

3. **Data Table**
   - Recent Data (Last 30 Days)
   - Shows: Date, NAV, Bid/Ask Price, Portfolio Value, Units

## Configuration Details

### docker-compose.test.yml

Complete stack with three services:

1. **influxdb** (port 8086)
   - Image: influxdb:2.7
   - Auto-initialized with setup mode
   - Creates org, bucket, and admin token automatically
   - Health checks enabled

2. **grafana** (port 3000)
   - Image: grafana/grafana:10.2.0
   - Auto-provisions datasource from `grafana-provisioning/datasources/`
   - Auto-loads dashboard from `grafana-provisioning/dashboards/`
   - Health checks enabled

3. **stock-monitor**
   - Built from local Dockerfile
   - Connected to InfluxDB via Docker network
   - Runs scheduler for daily updates at 12:00 PM CET

### Networking

- All services on custom bridge network: `monitoring`
- Inter-service communication via service names (e.g., `http://influxdb:8086`)
- External access via published ports

### Data Persistence

- InfluxDB data: Docker volume `influxdb-data`
- Grafana data: Docker volume `grafana-data`
- Application logs: Local directory `./logs`

## Testing Workflow

1. **Start services**: `./start-test.sh`
2. **Import data**: `./import-data.sh`
3. **View dashboard**: http://localhost:3000
4. **Verify data**: Check InfluxDB UI or Grafana panels
5. **Test manual update**: 
   ```bash
   docker-compose -f docker-compose.test.yml exec stock-monitor python3 /app/scripts/daily_update.py
   ```
6. **Stop when done**: `./stop-test.sh`

## Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker info

# Check port availability
lsof -i :3000
lsof -i :8086

# View logs
docker-compose -f docker-compose.test.yml logs
```

### Dashboard not appearing
```bash
# Restart Grafana
docker-compose -f docker-compose.test.yml restart grafana

# Check provisioning logs
docker-compose -f docker-compose.test.yml logs grafana | grep -i provision
```

### No data in charts
```bash
# Verify InfluxDB has data
docker-compose -f docker-compose.test.yml exec influxdb influx query 'from(bucket:"stocks") |> range(start:-7d) |> count()'

# Run backfill if needed
docker-compose -f docker-compose.test.yml exec stock-monitor python3 /app/scripts/backfill.py
```

## Differences from Production

| Aspect | Test Environment | Production |
|--------|-----------------|------------|
| InfluxDB | Included | External |
| Grafana | Included | External |
| Credentials | Hardcoded | Environment variables |
| Setup | Automated | Manual |
| Purpose | Development/Testing | Real monitoring |
| Data | Temporary | Persistent |

## Next Steps After Testing

1. Review the dashboard and customize as needed
2. Test with different fund IDs or unit amounts
3. Export dashboard JSON for production use
4. Set up production environment with `docker-compose.yml`
5. Configure real InfluxDB and Grafana instances
6. Use secure credentials from `.env` file

## Benefits of Test Environment

✅ **Zero Configuration** - Everything pre-configured
✅ **Fast Setup** - Running in under 1 minute
✅ **Complete Stack** - All components included
✅ **Easy Cleanup** - Remove everything with one command
✅ **Safe Testing** - Isolated from production
✅ **Learning Tool** - See how all parts work together

---

For detailed information, see [README.TEST.md](README.TEST.md)
