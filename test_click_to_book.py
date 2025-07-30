#!/usr/bin/env python3
"""
Test script for Click-to-Book Calendar functionality
Tests the new 5-minute time slot intervals and click-to-book features
"""

import requests
import json
from datetime import datetime, date, timedelta
import sys

# Configuration
BASE_URL = "http://localhost:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login():
    """Login and get session"""
    session = requests.Session()
    
    # Get login page to get CSRF token
    login_page = session.get(f"{BASE_URL}/auth/login")
    
    # Extract CSRF token (simplified - in real scenario you'd parse the HTML)
    csrf_token = "test_token"  # This would be extracted from the form
    
    # Login
    login_data = {
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD,
        'remember_me': False,
        'csrf_token': csrf_token
    }
    
    response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
    
    if response.status_code == 302:
        print("✅ Login successful")
        return session
    else:
        print("❌ Login failed")
        return None

def test_5_minute_time_slots():
    """Test that the calendar now shows 5-minute intervals"""
    print("\n🧪 Testing 5-minute time slots...")
    
    session = login()
    if not session:
        return False
    
    # Get the admin calendar page
    response = session.get(f"{BASE_URL}/appointments/admin-appointments")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for 5-minute intervals in the calendar
        # Look for time slots like 09:00, 09:05, 09:10, etc.
        expected_times = [
            "09:00", "09:05", "09:10", "09:15", "09:20", "09:25", "09:30", "09:35", "09:40", "09:45", "09:50", "09:55",
            "10:00", "10:05", "10:10", "10:15", "10:20", "10:25", "10:30", "10:35", "10:40", "10:45", "10:50", "10:55"
        ]
        
        found_times = []
        for time in expected_times:
            if time in content:
                found_times.append(time)
        
        if len(found_times) >= 10:  # At least 10 time slots should be found
            print(f"✅ Found {len(found_times)} 5-minute time slots: {found_times[:5]}...")
            return True
        else:
            print(f"❌ Only found {len(found_times)} time slots, expected more")
            return False
    else:
        print(f"❌ Failed to load calendar page: {response.status_code}")
        return False

def test_click_to_book_modal():
    """Test that click-to-book modal elements are present"""
    print("\n🧪 Testing click-to-book modal elements...")
    
    session = login()
    if not session:
        return False
    
    # Get the admin calendar page
    response = session.get(f"{BASE_URL}/appointments/admin-appointments")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for click-to-book JavaScript functions
        required_elements = [
            "handleTimeSlotClick",
            "showBookingModal", 
            "closeBookingModal",
            "redirectToBooking",
            "calendar-time-slot",
            "click-to-book-overlay",
            "click-to-book-modal"
        ]
        
        found_elements = []
        for element in required_elements:
            if element in content:
                found_elements.append(element)
        
        if len(found_elements) >= 5:  # At least 5 elements should be found
            print(f"✅ Found {len(found_elements)} click-to-book elements: {found_elements}")
            return True
        else:
            print(f"❌ Only found {len(found_elements)} elements, expected more")
            return False
    else:
        print(f"❌ Failed to load calendar page: {response.status_code}")
        return False

def test_booking_form_prefill():
    """Test that booking form can be pre-filled with parameters"""
    print("\n🧪 Testing booking form pre-fill functionality...")
    
    session = login()
    if not session:
        return False
    
    # Test booking form with pre-filled parameters
    test_date = date.today().isoformat()
    test_time = "10:00"
    test_stylist_id = "1"  # Assuming stylist ID 1 exists
    
    booking_url = f"{BASE_URL}/appointments/book?date={test_date}&time={test_time}&stylist_id={test_stylist_id}"
    response = session.get(booking_url)
    
    if response.status_code == 200:
        content = response.text
        
        # Check for pre-filled indicator
        if "Pre-filled from Calendar" in content:
            print("✅ Pre-filled indicator found")
            return True
        else:
            print("❌ Pre-filled indicator not found")
            return False
    else:
        print(f"❌ Failed to load booking form: {response.status_code}")
        return False

def test_form_time_slots():
    """Test that booking form has 5-minute time slots"""
    print("\n🧪 Testing booking form 5-minute time slots...")
    
    session = login()
    if not session:
        return False
    
    # Get the booking form
    response = session.get(f"{BASE_URL}/appointments/book")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for 5-minute intervals in the time dropdown
        expected_times = ["09:00", "09:05", "09:10", "09:15", "09:20", "09:25", "09:30", "09:35", "09:40", "09:45", "09:50", "09:55"]
        
        found_times = []
        for time in expected_times:
            if time in content:
                found_times.append(time)
        
        if len(found_times) >= 10:
            print(f"✅ Found {len(found_times)} 5-minute time slots in booking form: {found_times[:5]}...")
            return True
        else:
            print(f"❌ Only found {len(found_times)} time slots in booking form")
            return False
    else:
        print(f"❌ Failed to load booking form: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Click-to-Book Calendar Functionality")
    print("=" * 50)
    
    tests = [
        test_5_minute_time_slots,
        test_click_to_book_modal,
        test_booking_form_prefill,
        test_form_time_slots
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Click-to-book functionality is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 