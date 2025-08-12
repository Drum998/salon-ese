#!/usr/bin/env python3
"""
Test script to verify UK timezone functionality.
Run this to check that the timezone changes are working correctly.
"""

from app.utils import uk_now, uk_utcnow
from datetime import datetime, timedelta
import pytz

def test_timezone_functions():
    print("Testing UK Timezone Functions")
    print("=" * 40)
    
    # Test uk_now() - should return UK time
    uk_time = uk_now()
    print(f"UK Time (uk_now()): {uk_time}")
    print(f"UK Timezone: {uk_time.tzinfo}")
    print(f"UK Timezone Name: {uk_time.tzinfo.zone}")
    
    # Test uk_utcnow() - should return UTC time but based on UK time
    uk_utc_time = uk_utcnow()
    print(f"\nUK UTC Time (uk_utcnow()): {uk_utc_time}")
    print(f"UK UTC Timezone: {uk_utc_time.tzinfo}")
    
    # Compare with regular UTC
    regular_utc = datetime.now(pytz.UTC)
    print(f"\nRegular UTC: {regular_utc}")
    
    # Make sure uk_utc_time is timezone-aware for comparison
    if uk_utc_time.tzinfo is None:
        # If uk_utc_time is naive, assume it's UTC
        uk_utc_time = pytz.UTC.localize(uk_utc_time)
    
    # Show the difference (should be 0 or 1 hour depending on DST)
    time_diff = abs((uk_utc_time - regular_utc).total_seconds())
    print(f"\nTime difference between UK UTC and Regular UTC: {time_diff} seconds")
    
    if time_diff < 60:  # Less than 1 minute difference
        print("✓ UK timezone is working correctly!")
    else:
        print("⚠ Warning: There might be a timezone issue")
    
    # Show current DST status - use the datetime's dst() method directly
    is_dst = uk_time.dst() != timedelta(0)
    print(f"\nCurrent DST Status: {'BST (Daylight Saving)' if is_dst else 'GMT (Standard Time)'}")

if __name__ == "__main__":
    test_timezone_functions() 