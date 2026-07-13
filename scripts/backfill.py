#!/usr/bin/env python3
"""
Backfill script to import all historical fund data into InfluxDB.
Run this once to populate historical data from 2023-05-22 to present.
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

def fetch_fund_data():
    """Fetch all historical fund data from the API."""
    print(f"Fetching historical data for fund ID {FUND_ID}...")
    
    try:
        response = requests.get(f"{FUND_API_URL}?id={FUND_ID}", timeout=30)
        response.raise_for_status()
        data = response.json()
        
        rates = data.get('rates', [])
        print(f"Retrieved {len(rates)} historical data points")
        return rates
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        sys.exit(1)

def write_to_influxdb(rates):
    """Write all historical data points to InfluxDB."""
    print(f"Connecting to InfluxDB at {INFLUXDB_URL}...")
    
    try:
        client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        points = []
        for rate in rates:
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
            
            points.append(point)
        
        print(f"Writing {len(points)} data points to InfluxDB bucket '{INFLUXDB_BUCKET}'...")
        write_api.write(bucket=INFLUXDB_BUCKET, record=points)
        
        print(f"Successfully wrote {len(points)} data points to InfluxDB")
        client.close()
        
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")
        sys.exit(1)

def main():
    print("=" * 60)
    print("Fund Data Backfill Script")
    print("=" * 60)
    print(f"Fund ID: {FUND_ID}")
    print(f"Fund Name: {FUND_NAME}")
    print(f"Units Held: {UNITS_HELD}")
    print(f"InfluxDB URL: {INFLUXDB_URL}")
    print(f"InfluxDB Org: {INFLUXDB_ORG}")
    print(f"InfluxDB Bucket: {INFLUXDB_BUCKET}")
    print("=" * 60)
    
    # Fetch historical data
    rates = fetch_fund_data()
    
    if not rates:
        print("No data retrieved from API. Exiting.")
        sys.exit(1)
    
    # Write to InfluxDB
    write_to_influxdb(rates)
    
    print("=" * 60)
    print("Backfill completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
