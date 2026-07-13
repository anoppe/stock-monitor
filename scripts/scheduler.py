#!/usr/bin/env python3
"""
Scheduler script that runs the daily update at 12:00 PM CET every day.
Uses a Python loop with sleep for scheduling (no cron daemon needed).
"""

import os
import sys
import time
import subprocess
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo

# Configuration
TARGET_HOUR = int(os.getenv('UPDATE_HOUR', '12'))  # 12:00 PM by default
TARGET_MINUTE = int(os.getenv('UPDATE_MINUTE', '0'))
TIMEZONE = os.getenv('TIMEZONE', 'Europe/Amsterdam')  # CET/CEST

def get_seconds_until_next_run():
    """
    Calculate how many seconds until the next scheduled run time.
    Returns the number of seconds to sleep.
    """
    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)
    
    # Create target time for today
    target = now.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=0, microsecond=0)
    
    # If target time has already passed today, schedule for tomorrow
    if now >= target:
        # Add one day
        from datetime import timedelta
        target = target + timedelta(days=1)
    
    # Calculate seconds until target
    delta = (target - now).total_seconds()
    
    return delta, target

def run_daily_update():
    """Execute the daily update script."""
    print(f"\n{'='*60}")
    print(f"Running daily update at {datetime.now(ZoneInfo(TIMEZONE)).isoformat()}")
    print(f"{'='*60}")
    
    try:
        # Run the daily_update.py script
        result = subprocess.run(
            [sys.executable, '/app/scripts/daily_update.py'],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"Daily update completed successfully")
        else:
            print(f"Daily update failed with exit code {result.returncode}")
    
    except Exception as e:
        print(f"Error running daily update: {e}")
    
    print(f"{'='*60}\n")

def main():
    print("=" * 60)
    print("Fund Data Scheduler Started")
    print("=" * 60)
    print(f"Timezone: {TIMEZONE}")
    print(f"Target Time: {TARGET_HOUR:02d}:{TARGET_MINUTE:02d}")
    print(f"Current Time: {datetime.now(ZoneInfo(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("=" * 60)
    
    while True:
        # Calculate time until next run
        seconds_to_wait, next_run_time = get_seconds_until_next_run()
        
        print(f"\n[{datetime.now(ZoneInfo(TIMEZONE)).isoformat()}]")
        print(f"Next run scheduled for: {next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Sleeping for {seconds_to_wait:.0f} seconds ({seconds_to_wait/3600:.1f} hours)")
        
        # Sleep until next run time
        time.sleep(seconds_to_wait)
        
        # Run the daily update
        run_daily_update()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFatal error in scheduler: {e}")
        sys.exit(1)
