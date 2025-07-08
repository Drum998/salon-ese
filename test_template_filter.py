#!/usr/bin/env python3
"""
Test script to verify the template filter functionality.
"""

from app.utils import to_uk_timezone, uk_timezone_strftime
from datetime import datetime
import pytz

def test_template_filter():
    print("Testing Template Filter")
    print("=" * 30)
    
    # Create a UTC datetime
    utc_time = datetime.now(pytz.UTC)
    print(f"Original UTC time: {utc_time}")
    
    # Test the basic timezone filter
    uk_time = to_uk_timezone(utc_time)
    print(f"UK time (after filter): {uk_time}")
    
    # Test the combined strftime filter
    formatted_time = uk_timezone_strftime(utc_time, '%B %d, %Y at %I:%M %p')
    print(f"Formatted UK time: {formatted_time}")
    
    # Show the difference
    time_diff = (uk_time - utc_time.replace(tzinfo=pytz.UTC)).total_seconds() / 3600
    print(f"Time difference: {time_diff} hours")
    
    if abs(time_diff) <= 1:  # Should be 0 or 1 hour depending on DST
        print("✓ Template filter is working correctly!")
    else:
        print("⚠ Warning: Template filter might have an issue")
    
    # Test with naive datetime (should assume UTC)
    naive_time = datetime.now()
    print(f"\nNaive datetime: {naive_time}")
    uk_naive = to_uk_timezone(naive_time)
    print(f"UK time from naive: {uk_naive}")
    
    # Test with None
    none_result = to_uk_timezone(None)
    print(f"\nNone input result: {none_result}")
    
    # Test the strftime filter with None
    none_strftime = uk_timezone_strftime(None, '%B %d, %Y')
    print(f"None strftime result: {none_strftime}")

if __name__ == "__main__":
    test_template_filter() 