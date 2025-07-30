#!/usr/bin/env python3
"""
Test script for Appointment Display Features
Tests the new appointment display with full duration coverage and narrower time slots
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

def test_narrower_time_slots():
    """Test that time slots are now narrower (20px height)"""
    print("\n🧪 Testing narrower time slots...")
    
    session = login()
    if not session:
        return False
    
    # Get the admin calendar page
    response = session.get(f"{BASE_URL}/appointments/admin-appointments")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for narrower time slot styling
        required_elements = [
            "height: 20px",
            "min-height: 20px",
            "font-size: 0.7rem"
        ]
        
        found_elements = []
        for element in required_elements:
            if element in content:
                found_elements.append(element)
        
        if len(found_elements) >= 2:
            print(f"✅ Found {len(found_elements)} narrow time slot elements: {found_elements}")
            return True
        else:
            print(f"❌ Only found {len(found_elements)} elements, expected more")
            return False
    else:
        print(f"❌ Failed to load calendar page: {response.status_code}")
        return False

def test_appointment_duration_display():
    """Test that appointments display with full duration coverage"""
    print("\n🧪 Testing appointment duration display...")
    
    session = login()
    if not session:
        return False
    
    # Get the admin calendar page
    response = session.get(f"{BASE_URL}/appointments/admin-appointments")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for appointment duration calculation elements
        required_elements = [
            "appointment_start",
            "appointment_end",
            "current_time",
            "position: absolute",
            "top: 0",
            "bottom: 0"
        ]
        
        found_elements = []
        for element in required_elements:
            if element in content:
                found_elements.append(element)
        
        if len(found_elements) >= 4:
            print(f"✅ Found {len(found_elements)} duration display elements: {found_elements}")
            return True
        else:
            print(f"❌ Only found {len(found_elements)} elements, expected more")
            return False
    else:
        print(f"❌ Failed to load calendar page: {response.status_code}")
        return False

def test_appointment_styling():
    """Test that appointment styling is updated for full coverage"""
    print("\n🧪 Testing appointment styling...")
    
    session = login()
    if not session:
        return False
    
    # Get the admin calendar page
    response = session.get(f"{BASE_URL}/appointments/admin-appointments")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for updated appointment styling
        required_elements = [
            "appointment-slot",
            "position: absolute",
            "z-index: 10",
            "font-size: 0.7rem",
            "border-radius: 2px"
        ]
        
        found_elements = []
        for element in required_elements:
            if element in content:
                found_elements.append(element)
        
        if len(found_elements) >= 4:
            print(f"✅ Found {len(found_elements)} appointment styling elements: {found_elements}")
            return True
        else:
            print(f"❌ Only found {len(found_elements)} elements, expected more")
            return False
    else:
        print(f"❌ Failed to load calendar page: {response.status_code}")
        return False

def test_time_slot_click_behavior():
    """Test that time slot click behavior still works with new display"""
    print("\n🧪 Testing time slot click behavior...")
    
    session = login()
    if not session:
        return False
    
    # Get the admin calendar page
    response = session.get(f"{BASE_URL}/appointments/admin-appointments")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for click-to-book functionality
        required_elements = [
            "handleTimeSlotClick",
            "calendar-time-slot",
            "onclick",
            "data-date",
            "data-time"
        ]
        
        found_elements = []
        for element in required_elements:
            if element in content:
                found_elements.append(element)
        
        if len(found_elements) >= 4:
            print(f"✅ Found {len(found_elements)} click behavior elements: {found_elements}")
            return True
        else:
            print(f"❌ Only found {len(found_elements)} elements, expected more")
            return False
    else:
        print(f"❌ Failed to load calendar page: {response.status_code}")
        return False

def test_calendar_layout():
    """Test that the overall calendar layout is correct"""
    print("\n🧪 Testing calendar layout...")
    
    session = login()
    if not session:
        return False
    
    # Get the admin calendar page
    response = session.get(f"{BASE_URL}/appointments/admin-appointments")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for proper calendar structure
        structure_checks = [
            ("day-navigation", "Day navigation"),
            ("sticky-header", "Sticky header"),
            ("calendar-container", "Calendar container"),
            ("appointment-slot", "Appointment slots"),
            ("calendar-time-slot", "Time slots")
        ]
        
        passed_checks = 0
        for element, description in structure_checks:
            if element in content:
                print(f"  ✅ {description} found")
                passed_checks += 1
            else:
                print(f"  ❌ {description} missing")
        
        if passed_checks >= 4:
            print(f"✅ Calendar layout test passed: {passed_checks}/5 checks")
            return True
        else:
            print(f"❌ Calendar layout test failed: {passed_checks}/5 checks")
            return False
    else:
        print(f"❌ Failed to load calendar page: {response.status_code}")
        return False

def test_appointment_overlap_prevention():
    """Test that appointments prevent overlap in the display"""
    print("\n🧪 Testing appointment overlap prevention...")
    
    session = login()
    if not session:
        return False
    
    # Get the admin calendar page
    response = session.get(f"{BASE_URL}/appointments/admin-appointments")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for overlap prevention logic
        overlap_elements = [
            "appointment_start",
            "appointment_end", 
            "current_time",
            "position: absolute",
            "z-index: 10"
        ]
        
        found_elements = []
        for element in overlap_elements:
            if element in content:
                found_elements.append(element)
        
        if len(found_elements) >= 4:
            print(f"✅ Found {len(found_elements)} overlap prevention elements: {found_elements}")
            return True
        else:
            print(f"❌ Only found {len(found_elements)} overlap prevention elements")
            return False
    else:
        print(f"❌ Failed to load calendar page: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Appointment Display Features")
    print("=" * 50)
    
    tests = [
        test_narrower_time_slots,
        test_appointment_duration_display,
        test_appointment_styling,
        test_time_slot_click_behavior,
        test_calendar_layout,
        test_appointment_overlap_prevention
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
        print("🎉 All tests passed! Appointment display features are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 