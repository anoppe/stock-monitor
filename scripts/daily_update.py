#!/usr/bin/env python3
"""
Daily update script to fetch the latest fund data and write to InfluxDB.
This script fetches only the most recent data point.
"""

import os
import sys
import requests
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration from environment variables
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'YOUR_TOKEN_HERE')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'YOUR_ORG_HERE')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'YOUR_BUCKET_HERE')

FUND_API_URL = os.getenv('FUND_API_URL', 'https://devrobotapi.azurewebsites.net/v1/fundrates')
FUND_ID = os.getenv('FUND_ID', '8015')
FUND_NAME = os.getenv('FUND_NAME', 'BND_Wereld_Indexfonds_Totaal_Carbon_Screened')
UNITS_HELD = float(os.getenv('UNITS_HELD', '12.0'))

def fetch_latest_data():
    """Fetch the latest fund data from the API."""
    print(f"[{datetime.now().isoformat()}] Fetching latest data for fund ID {FUND_ID}...")
    
    try:
        response = requests.get(f"{FUND_API_URL}?id={FUND_ID}", timeout=30)
        response.raise_for_status()
        data = response.json()
        
        rates = data.get('rates', [])
        if not rates:
            print("No data returned from API")
            return None
        
        # The API returns data in reverse chronological order (newest first)
        latest = rates[0]
        print(f"Retrieved latest data point: {latest['date']} - NAV: €{latest['nav']:.2f}")
        return latest
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

def write_to_influxdb(rate):
    """Write the latest data point to InfluxDB."""
    try:
        client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        # Parse the date from API response
        timestamp = datetime.fromisoformat(rate['date'].replace('Z', '+00:00'))
        
        nav = rate['nav']
        portfolio_value = nav * UNITS_HELD
        
        # Create InfluxDB point
        point = Point("fund_performance") \
            .tag("fund_id", FUND_ID) \
            .tag("fund_name", FUND_NAME) \
            .field("nav", nav) \
            .field("bid_price", rate['bidPrice']) \
            .field("ask_price", rate['askPrice']) \
            .field("units_held", UNITS_HELD) \
            .field("portfolio_value", portfolio_value) \
            .time(timestamp)
        
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        
        print(f"[{datetime.now().isoformat()}] Successfully wrote data to InfluxDB:")
        print(f"  - Date: {timestamp.isoformat()}")
        print(f"  - NAV: €{nav:.2f}")
        print(f"  - Units: {UNITS_HELD}")
        print(f"  - Portfolio Value: €{portfolio_value:.2f}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")
        return False

def main():
    # Fetch latest data
    latest = fetch_latest_data()
    
    if not latest:
        print("Failed to retrieve data. Exiting.")
        sys.exit(1)
    
    # Write to InfluxDB
    success = write_to_influxdb(latest)
    
    if success:
        print(f"[{datetime.now().isoformat()}] Daily update completed successfully!")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
