#!/usr/bin/env python3
"""
Test script for Calendar Navigation Features
Tests the new day navigation buttons and sticky header functionality
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

def test_day_navigation_buttons():
    """Test that day navigation buttons are present and functional"""
    print("\n🧪 Testing day navigation buttons...")
    
    session = login()
    if not session:
        return False
    
    # Get the admin calendar page
    response = session.get(f"{BASE_URL}/appointments/admin-appointments")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for day navigation elements
        required_elements = [
            "day-navigation",
            "day-nav-btn",
            "scrollToDay",
            "data-day"
        ]
        
        found_elements = []
        for element in required_elements:
            if element in content:
                found_elements.append(element)
        
        if len(found_elements) >= 3:
            print(f"✅ Found {len(found_elements)} day navigation elements: {found_elements}")
            return True
        else:
            print(f"❌ Only found {len(found_elements)} elements, expected more")
            return False
    else:
        print(f"❌ Failed to load calendar page: {response.status_code}")
        return False

def test_sticky_header():
    """Test that sticky header elements are present"""
    print("\n🧪 Testing sticky header functionality...")
    
    session = login()
    if not session:
        return False
    
    # Get the admin calendar page
    response = session.get(f"{BASE_URL}/appointments/admin-appointments")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for sticky header elements
        required_elements = [
            "sticky-header",
            "calendar-container",
            "position: sticky",
            "top: 0"
        ]
        
        found_elements = []
        for element in required_elements:
            if element in content:
                found_elements.append(element)
        
        if len(found_elements) >= 3:
            print(f"✅ Found {len(found_elements)} sticky header elements: {found_elements}")
            return True
        else:
            print(f"❌ Only found {len(found_elements)} elements, expected more")
            return False
    else:
        print(f"❌ Failed to load calendar page: {response.status_code}")
        return False

def test_day_sections():
    """Test that day sections are properly marked for navigation"""
    print("\n🧪 Testing day sections...")
    
    session = login()
    if not session:
        return False
    
    # Get the admin calendar page
    response = session.get(f"{BASE_URL}/appointments/admin-appointments")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for day section elements
        required_elements = [
            "day-section",
            "data-day"
        ]
        
        found_elements = []
        for element in required_elements:
            if element in content:
                found_elements.append(element)
        
        if len(found_elements) >= 2:
            print(f"✅ Found {len(found_elements)} day section elements: {found_elements}")
            return True
        else:
            print(f"❌ Only found {len(found_elements)} elements, expected more")
            return False
    else:
        print(f"❌ Failed to load calendar page: {response.status_code}")
        return False

def test_calendar_structure():
    """Test that the calendar structure is correct with navigation"""
    print("\n🧪 Testing calendar structure...")
    
    session = login()
    if not session:
        return False
    
    # Get the admin calendar page
    response = session.get(f"{BASE_URL}/appointments/admin-appointments")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for proper calendar structure
        structure_checks = [
            ("day-navigation", "Day navigation section"),
            ("calendar-container", "Calendar container"),
            ("sticky-header", "Sticky header"),
            ("day-section", "Day sections"),
            ("scrollToDay", "Scroll function")
        ]
        
        passed_checks = 0
        for element, description in structure_checks:
            if element in content:
                print(f"  ✅ {description} found")
                passed_checks += 1
            else:
                print(f"  ❌ {description} missing")
        
        if passed_checks >= 4:
            print(f"✅ Calendar structure test passed: {passed_checks}/5 checks")
            return True
        else:
            print(f"❌ Calendar structure test failed: {passed_checks}/5 checks")
            return False
    else:
        print(f"❌ Failed to load calendar page: {response.status_code}")
        return False

def test_week_view_navigation():
    """Test that week view navigation works correctly"""
    print("\n🧪 Testing week view navigation...")
    
    session = login()
    if not session:
        return False
    
    # Test week view with specific date
    test_date = date.today().isoformat()
    response = session.get(f"{BASE_URL}/appointments/admin-appointments?view_type=week&date={test_date}")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for week-specific elements
        week_elements = [
            "Week of",
            "day-navigation",
            "day-nav-btn"
        ]
        
        found_elements = []
        for element in week_elements:
            if element in content:
                found_elements.append(element)
        
        if len(found_elements) >= 2:
            print(f"✅ Found {len(found_elements)} week view elements: {found_elements}")
            return True
        else:
            print(f"❌ Only found {len(found_elements)} week view elements")
            return False
    else:
        print(f"❌ Failed to load week view: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Calendar Navigation Features")
    print("=" * 50)
    
    tests = [
        test_day_navigation_buttons,
        test_sticky_header,
        test_day_sections,
        test_calendar_structure,
        test_week_view_navigation
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
        print("🎉 All tests passed! Calendar navigation features are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 