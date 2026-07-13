# Stock Monitor for InfluxDB + Grafana

Automated monitoring system for BrandNewDay investment funds. Fetches daily NAV (Net Asset Value) data and stores it in InfluxDB for visualization in Grafana.

## Features

- **Automated daily data collection** at 12:00 PM CET
- **Historical data backfill** from 2023-05-22 to present
- **Portfolio value tracking** (units × NAV)
- **Docker container** for easy deployment via Portainer
- **Python scheduler** (no cron daemon needed)

## Architecture

```
Fund API → Python Scripts → InfluxDB → Grafana
```

**Components:**
- `backfill.py` - One-time import of historical data
- `daily_update.py` - Fetch latest data point
- `scheduler.py` - Main loop that runs daily at 12:00 PM CET
- Docker container with Python 3.11 + dependencies

## 🧪 Test Environment (Recommended for First-Time Users)

**Want to try it out immediately?** Use our pre-configured test environment with InfluxDB and Grafana included!

```bash
# Start the complete test environment
./start-test.sh

# Import historical data
./import-data.sh

# Open Grafana dashboard at http://localhost:3000
# Login: admin / admin
```

**See [README.TEST.md](README.TEST.md) for complete test environment documentation.**

The test environment includes:
- ✅ Pre-configured InfluxDB with automatic setup
- ✅ Pre-configured Grafana with ready-to-use dashboard
- ✅ Stock Monitor application connected and running
- ✅ No manual configuration needed!

---

## Production Deployment

### Quick Start

### 1. Clone and Configure

```bash
cd stock-monitor

# Copy environment template
cp .env.template .env

# Edit .env with your InfluxDB details
nano .env
```

### 2. Configure Environment Variables

Edit `.env` and replace the placeholders:

```bash
# InfluxDB Configuration
INFLUXDB_URL=http://influxdb:8086          # Your InfluxDB URL
INFLUXDB_TOKEN=your_actual_token_here       # Generate in InfluxDB UI
INFLUXDB_ORG=your_organization_name         # Your InfluxDB org
INFLUXDB_BUCKET=stocks                      # Bucket name (create in InfluxDB)

# Fund Configuration
UNITS_HELD=12.0                             # Your actual units held
```

### 3. Deploy with Docker Compose

```bash
# Build and start the container
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 4. Run Historical Backfill (One-time)

After the container is running, import all historical data:

```bash
docker-compose exec stock-monitor python3 /app/scripts/backfill.py
```

This will import ~3 years of historical data (2023-05-22 to present).

## Portainer Deployment

1. **In Portainer**, go to **Stacks** → **Add Stack**
2. **Upload** or paste the `docker-compose.yml` content
3. **Add environment variables** from `.env` in the Portainer UI
4. **Deploy the stack**
5. **Execute backfill** via Portainer console:
   - Select the `stock-monitor` container
   - Go to **Console**
   - Run: `python3 /app/scripts/backfill.py`

## InfluxDB Setup

### Create Bucket and Token

1. Open InfluxDB UI (usually http://localhost:8086)
2. Go to **Data** → **Buckets** → **Create Bucket**
   - Name: `stocks` (or any name, update `.env`)
3. Go to **Data** → **API Tokens** → **Generate API Token**
   - Type: **Read/Write Token**
   - Bucket: `stocks`
4. Copy the token to your `.env` file

### Data Schema

The scripts write data to InfluxDB with this structure:

```
Measurement: fund_performance

Tags:
  - fund_id: 8015
  - fund_name: BND_Wereld_Indexfonds_Totaal_Carbon_Screened

Fields:
  - nav (float): Net Asset Value per unit
  - bid_price (float): Bid price
  - ask_price (float): Ask price
  - units_held (float): Number of units you own
  - portfolio_value (float): Total value (nav × units_held)

Timestamp: Date from API
```

## Grafana Dashboard

### Connect InfluxDB to Grafana

1. In Grafana, go to **Configuration** → **Data Sources** → **Add data source**
2. Select **InfluxDB**
3. Configure:
   - **Query Language**: Flux
   - **URL**: `http://influxdb:8086`
   - **Organization**: (your org from `.env`)
   - **Token**: (your token from `.env`)
   - **Default Bucket**: `stocks`
4. **Save & Test**

### Sample Flux Queries

**Portfolio Value Over Time:**
```flux
from(bucket: "stocks")
  |> range(start: -1y)
  |> filter(fn: (r) => r._measurement == "fund_performance")
  |> filter(fn: (r) => r._field == "portfolio_value")
```

**NAV (Unit Price) Over Time:**
```flux
from(bucket: "stocks")
  |> range(start: -1y)
  |> filter(fn: (r) => r._measurement == "fund_performance")
  |> filter(fn: (r) => r._field == "nav")
```

**Daily Change (%):**
```flux
from(bucket: "stocks")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "fund_performance")
  |> filter(fn: (r) => r._field == "nav")
  |> derivative(unit: 1d, nonNegative: false)
  |> map(fn: (r) => ({ r with _value: r._value / r._value * 100.0 }))
```

## Configuration Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `INFLUXDB_URL` | InfluxDB server URL | `http://localhost:8086` |
| `INFLUXDB_TOKEN` | InfluxDB authentication token | (required) |
| `INFLUXDB_ORG` | InfluxDB organization name | (required) |
| `INFLUXDB_BUCKET` | InfluxDB bucket name | (required) |
| `FUND_API_URL` | Fund data API endpoint | `https://devrobotapi.azurewebsites.net/v1/fundrates` |
| `FUND_ID` | Fund identifier | `8015` |
| `FUND_NAME` | Fund display name | `BND_Wereld_Indexfonds_Totaal_Carbon_Screened` |
| `UNITS_HELD` | Number of fund units you own | `12.0` |
| `UPDATE_HOUR` | Hour to run daily update (24h) | `12` |
| `UPDATE_MINUTE` | Minute to run daily update | `0` |
| `TIMEZONE` | Timezone for scheduling | `Europe/Amsterdam` |

## Troubleshooting

### Check Container Logs

```bash
docker-compose logs -f stock-monitor
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
print('InfluxDB connection: OK' if client.ping() else 'FAILED')
client.close()
"
```

### Test Fund API

```bash
curl "https://devrobotapi.azurewebsites.net/v1/fundrates?id=8015" | python3 -m json.tool | head -30
```

### Run Daily Update Manually

```bash
docker-compose exec stock-monitor python3 /app/scripts/daily_update.py
```

### Check Scheduler Status

```bash
# View next scheduled run time
docker-compose logs stock-monitor | grep "Next run scheduled"
```

## Updating Units Held

When you buy or sell units:

1. Update `UNITS_HELD` in `.env`
2. Restart the container:
   ```bash
   docker-compose restart
   ```

The next update will use the new unit count. Historical data is not automatically recalculated.

## Maintenance

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

### Update Scripts

If you modify the Python scripts:

```bash
# Rebuild and restart
docker-compose up -d --build
```

## Data API

The system uses the BrandNewDay fund data API:

- **List all funds**: `https://devrobotapi.azurewebsites.net/v1/funds`
- **Fund rates**: `https://devrobotapi.azurewebsites.net/v1/fundrates?id={FUND_ID}`

Data updates once daily around 11:00 AM CET.

## License

MIT License - Feel free to modify and use as needed.

## Support

For issues or questions, check:
1. Docker container logs
2. InfluxDB connection
3. Fund API availability
4. Environment variable configuration
