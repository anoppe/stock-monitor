# Stock Monitor - Test Environment

This is a complete, self-contained test environment with InfluxDB, Grafana, and the Stock Monitor application pre-configured and ready to run.

## 🚀 Quick Start

### Start the Test Environment

```bash
# Start all services (InfluxDB, Grafana, Stock Monitor)
docker-compose -f docker-compose.test.yml up -d

# Watch the logs
docker-compose -f docker-compose.test.yml logs -f
```

### Access the Services

After starting, wait ~30 seconds for services to initialize, then access:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana Dashboard** | http://localhost:3000 | admin / admin |
| **InfluxDB UI** | http://localhost:8086 | admin / adminpassword123 |

The Grafana dashboard will be **automatically provisioned** and ready to view!

## 📊 What You Get

### Pre-configured Services

1. **InfluxDB 2.7**
   - Organization: `stock-monitor`
   - Bucket: `stocks`
   - Token: `test-token-stock-monitor-12345`
   - Auto-initialized on first run

2. **Grafana 10.2**
   - Pre-configured InfluxDB datasource
   - Auto-loaded "Stock Monitor - Fund Performance" dashboard
   - Dark theme enabled

3. **Stock Monitor Application**
   - Tracks fund ID 8015 (BND Wereld Indexfonds)
   - 12.0 units held
   - Daily updates at 12:00 PM CET
   - Connected to InfluxDB

### Dashboard Panels

The pre-configured dashboard includes:

1. **Current Portfolio Value** - Total value of your holdings
2. **Current NAV** - Latest unit price
3. **30-Day Return %** - Performance over last 30 days
4. **Units Held** - Number of fund units
5. **Portfolio Value Chart** - 1-year trend
6. **NAV Price Chart** - 1-year unit price trend
7. **Recent Data Table** - Last 30 days of data points

## 🔄 Import Historical Data

After the services are running, import historical data:

```bash
# Run the backfill script to import ~3 years of data
docker-compose -f docker-compose.test.yml exec stock-monitor python3 /app/scripts/backfill.py
```

This will import data from 2023-05-22 to present. The Grafana dashboard will automatically show all historical data.

## 📝 Testing Workflow

### 1. Initial Setup (First Time)

```bash
# Start services
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be healthy (~30 seconds)
docker-compose -f docker-compose.test.yml ps

# Import historical data
docker-compose -f docker-compose.test.yml exec stock-monitor python3 /app/scripts/backfill.py
```

### 2. View Dashboard

1. Open http://localhost:3000
2. Login with `admin` / `admin`
3. The dashboard "Stock Monitor - Fund Performance" will be on the home page
4. Click to view your data visualization

### 3. Verify Data in InfluxDB

```bash
# Access InfluxDB container
docker-compose -f docker-compose.test.yml exec influxdb influx

# Run a query (in InfluxDB shell)
> from(bucket: "stocks") |> range(start: -7d) |> filter(fn: (r) => r._measurement == "fund_performance")
```

Or use the InfluxDB UI at http://localhost:8086:
1. Login with `admin` / `adminpassword123`
2. Go to **Data Explorer**
3. Select bucket `stocks`
4. Query the data

### 4. Test Manual Data Fetch

```bash
# Manually trigger a data update
docker-compose -f docker-compose.test.yml exec stock-monitor python3 /app/scripts/daily_update.py

# Check the logs
docker-compose -f docker-compose.test.yml logs stock-monitor
```

## 🛠️ Configuration

### Default Test Configuration

The test environment uses these pre-configured values:

```bash
# InfluxDB
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=test-token-stock-monitor-12345
INFLUXDB_ORG=stock-monitor
INFLUXDB_BUCKET=stocks

# Fund Settings
FUND_ID=8015
FUND_NAME=BND_Wereld_Indexfonds_Totaal_Carbon_Screened
UNITS_HELD=12.0

# Schedule
UPDATE_HOUR=12
UPDATE_MINUTE=0
TIMEZONE=Europe/Amsterdam
```

### Customize for Testing

Edit `docker-compose.test.yml` to change:
- `UNITS_HELD` - Test with different unit amounts
- `FUND_ID` - Test with different funds
- `UPDATE_HOUR` / `UPDATE_MINUTE` - Change update time

Then restart:

```bash
docker-compose -f docker-compose.test.yml restart stock-monitor
```

## 🔍 Monitoring & Debugging

### Check Service Status

```bash
# View all services status
docker-compose -f docker-compose.test.yml ps

# Check health of services
docker-compose -f docker-compose.test.yml exec influxdb influx ping
docker-compose -f docker-compose.test.yml exec grafana wget -q -O- http://localhost:3000/api/health
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.test.yml logs -f

# Specific service
docker-compose -f docker-compose.test.yml logs -f stock-monitor
docker-compose -f docker-compose.test.yml logs -f influxdb
docker-compose -f docker-compose.test.yml logs -f grafana
```

### Verify Data Collection

```bash
# Check scheduler is running
docker-compose -f docker-compose.test.yml logs stock-monitor | grep "Next run scheduled"

# Check data points in InfluxDB
docker-compose -f docker-compose.test.yml exec influxdb influx query 'from(bucket:"stocks") |> range(start:-1d) |> count()'
```

## 🧹 Cleanup & Reset

### Stop Services (Keep Data)

```bash
docker-compose -f docker-compose.test.yml stop
```

### Stop and Remove Containers (Keep Data)

```bash
docker-compose -f docker-compose.test.yml down
```

### Complete Reset (Delete All Data)

```bash
# Stop and remove everything including volumes
docker-compose -f docker-compose.test.yml down -v

# Start fresh
docker-compose -f docker-compose.test.yml up -d
```

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check if ports are already in use
lsof -i :3000  # Grafana
lsof -i :8086  # InfluxDB

# Check logs for errors
docker-compose -f docker-compose.test.yml logs
```

### No Data in Grafana

1. **Check InfluxDB has data:**
   ```bash
   docker-compose -f docker-compose.test.yml exec influxdb influx query 'from(bucket:"stocks") |> range(start:-30d) |> count()'
   ```

2. **Verify datasource connection:**
   - Go to Grafana → Configuration → Data Sources
   - Click "InfluxDB-Stocks"
   - Click "Save & Test"

3. **Run backfill if needed:**
   ```bash
   docker-compose -f docker-compose.test.yml exec stock-monitor python3 /app/scripts/backfill.py
   ```

### Dashboard Not Auto-Loading

1. Restart Grafana:
   ```bash
   docker-compose -f docker-compose.test.yml restart grafana
   ```

2. Manually import dashboard:
   - Grafana → Dashboards → Import
   - Upload `grafana-provisioning/dashboards/stock-monitor-dashboard.json`

### Stock Monitor Not Updating

```bash
# Check if scheduler is running
docker-compose -f docker-compose.test.yml exec stock-monitor ps aux | grep scheduler

# Check environment variables
docker-compose -f docker-compose.test.yml exec stock-monitor env | grep INFLUX

# Manually run update
docker-compose -f docker-compose.test.yml exec stock-monitor python3 /app/scripts/daily_update.py
```

## 📦 Project Structure

```
stock-monitor/
├── docker-compose.test.yml                    # Test environment compose file
├── grafana-provisioning/
│   ├── datasources/
│   │   └── influxdb.yml                      # Auto-configured InfluxDB datasource
│   └── dashboards/
│       ├── dashboard-provider.yml            # Dashboard auto-loader
│       └── stock-monitor-dashboard.json      # Pre-built dashboard
├── scripts/
│   ├── scheduler.py                          # Daily scheduler
│   ├── daily_update.py                       # Fetch latest data
│   └── backfill.py                          # Import historical data
├── Dockerfile                                 # Stock monitor container
└── README.TEST.md                            # This file
```

## 🎯 Use Cases

### Development & Testing

```bash
# Quick test of changes
docker-compose -f docker-compose.test.yml up --build -d

# View immediate results
open http://localhost:3000
```

### Demo Environment

```bash
# Start everything
docker-compose -f docker-compose.test.yml up -d

# Import data
docker-compose -f docker-compose.test.yml exec stock-monitor python3 /app/scripts/backfill.py

# Show to stakeholders
open http://localhost:3000
```

### Integration Testing

```bash
# Start services
docker-compose -f docker-compose.test.yml up -d

# Run your tests
pytest tests/

# Cleanup
docker-compose -f docker-compose.test.yml down -v
```

## 🔐 Security Notes

⚠️ **This is a TEST environment only!**

- Uses hardcoded credentials
- Token is visible in compose file
- NOT suitable for production
- No SSL/TLS encryption
- No authentication beyond basic login

For production deployment, use `docker-compose.yml` with proper secrets management.

## 🆚 Test vs Production

| Feature | Test Environment | Production |
|---------|-----------------|------------|
| InfluxDB | Included, auto-setup | External, manual setup |
| Grafana | Included, auto-setup | External, manual setup |
| Credentials | Hardcoded | Environment variables |
| Volumes | Docker volumes | Persistent storage |
| Networking | Bridge network | Custom network |
| Dashboard | Auto-provisioned | Manual import |

## 📚 Next Steps

After testing successfully:

1. Use `docker-compose.yml` for production deployment
2. Create `.env` file with real credentials
3. Connect to your production InfluxDB/Grafana instances
4. Import the dashboard JSON manually from `grafana-provisioning/dashboards/`
5. Set up proper backup strategy
6. Configure alerting in Grafana

## 💡 Tips

- **Data persists** between container restarts (stored in Docker volumes)
- **Grafana changes** to the dashboard will persist
- **Schedule runs once daily** at 12:00 PM CET
- **Historical data** goes back to 2023-05-22
- **Refresh** Grafana dashboard to see new data (auto-refresh every 5 minutes)

---

**Questions?** Check the main [README.md](README.md) for detailed documentation.
