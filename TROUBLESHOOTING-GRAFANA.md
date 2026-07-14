# Debugging the 30-Day Return % Panel

## Problem

The 30-Day Return % panel is showing no data. This is likely due to the complex Flux query using `findRecord()`.

## Debugging Steps

### 1. Check if Data Exists

In Grafana Data Explorer (or InfluxDB UI):

```flux
from(bucket: "stocks")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "fund_performance")
  |> filter(fn: (r) => r._field == "nav")
  |> count()
```

**Expected**: Should return a count > 0 if you have data in the last 30 days.

### 2. View Raw NAV Data

```flux
from(bucket: "stocks")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "fund_performance")
  |> filter(fn: (r) => r._field == "nav")
```

**Expected**: Should show daily NAV values.

### 3. Test Simple Calculation

```flux
from(bucket: "stocks")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "fund_performance")
  |> filter(fn: (r) => r._field == "nav")
  |> last()
```

**Expected**: Should show the most recent NAV value.

## Solution: Simplified Query

Replace the query in the **30-Day Return %** panel with this simpler version:

### Option 1: Using difference() (Recommended)

```flux
from(bucket: "stocks")
  |> range(start: -31d, stop: now())
  |> filter(fn: (r) => r._measurement == "fund_performance")
  |> filter(fn: (r) => r._field == "nav")
  |> aggregateWindow(every: 1d, fn: last, createEmpty: false)
  |> difference(nonNegative: false)
  |> map(fn: (r) => ({ r with _value: r._value / r._value * 100.0 }))
  |> last()
```

### Option 2: Simple Comparison (Most Reliable)

```flux
import "experimental"

// Get first value from 30 days ago
first = from(bucket: "stocks")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "fund_performance")
  |> filter(fn: (r) => r._field == "nav")
  |> first()
  |> findRecord(fn: (key) => true, idx: 0)

// Get last value
last = from(bucket: "stocks")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "fund_performance")
  |> filter(fn: (r) => r._field == "nav")
  |> last()
  |> findRecord(fn: (key) => true, idx: 0)

// Calculate percentage
returnPct = (last._value - first._value) / first._value * 100.0

// Return as single value
array.from(rows: [{_time: now(), _value: returnPct}])
```

### Option 3: Simplest (No Calculation, Just Show Change)

```flux
from(bucket: "stocks")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "fund_performance")
  |> filter(fn: (r) => r._field == "nav")
  |> aggregateWindow(every: 30d, fn: mean, createEmpty: false)
  |> derivative(unit: 30d, nonNegative: false)
```

## How to Fix in Grafana

1. **Open Grafana** → http://localhost:3000
2. **Open Dashboard** → "Stock Monitor - Fund Performance"
3. **Edit Panel** → Click on "30-Day Return %" title → Edit
4. **Replace Query**:
   - Click on "Query" tab
   - Delete existing query
   - Paste one of the simplified queries above (try Option 2 first)
5. **Test** → Click "Run queries" button
6. **Save** → Click "Apply" then "Save dashboard"

## Alternative: Show Last 30 Days Average Instead

If the percentage calculation continues to fail, you can change the panel to show the average NAV over 30 days:

```flux
from(bucket: "stocks")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "fund_performance")
  |> filter(fn: (r) => r._field == "nav")
  |> mean()
```

Update panel title to "30-Day Average NAV" and change unit from "percent" to "currencyEUR".

## Common Issues

### Issue 1: Not Enough Data Points

If you have fewer than 30 days of data, the query will fail.

**Solution**: Change `start: -30d` to a shorter period like `-7d` or `-14d`.

### Issue 2: Data Gaps

If there are gaps in your data (weekends, holidays), `first()` might not get exactly 30 days ago.

**Solution**: Use `aggregateWindow()` to fill gaps or adjust the time range.

### Issue 3: Timezone Issues

InfluxDB times might not match your local timezone.

**Solution**: Ensure data exists by checking with a wider range:
```flux
from(bucket: "stocks")
  |> range(start: -60d)  // Check last 60 days
  |> filter(fn: (r) => r._measurement == "fund_performance")
  |> filter(fn: (r) => r._field == "nav")
```

## Test Environment Commands

If you need to restart the test environment and verify data:

```bash
# Start test environment
./start-test.sh

# Import data (if not already imported)
docker-compose -f docker-compose.test.yml exec stock-monitor python3 /app/scripts/backfill.py

# Check data in InfluxDB
docker-compose -f docker-compose.test.yml exec influxdb influx query 'from(bucket:"stocks") |> range(start:-30d) |> filter(fn: (r) => r._field == "nav") |> count()'

# View last 10 NAV values
docker-compose -f docker-compose.test.yml exec influxdb influx query 'from(bucket:"stocks") |> range(start:-30d) |> filter(fn: (r) => r._field == "nav") |> sort(columns:["_time"], desc:true) |> limit(n:10)'
```

## Recommendation

**Try Option 2 first** (Simple Comparison) as it's the most explicit and easiest to debug. If that doesn't work, check if you actually have 30 days of data with the debugging steps above.

If you need help, check:
1. Do you have data in the last 30 days?
2. Does the simpler query work?
3. What error message do you see in Grafana?
