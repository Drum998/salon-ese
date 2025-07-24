#!/usr/bin/env python3
"""
Test script for the stylist calendar view toggle functionality.
This script tests the new global vs personal calendar view feature.
"""

import requests
import json
from datetime import datetime, date

# Configuration
BASE_URL = "http://localhost:5010"
TEST_USERNAME = "test_stylist"
TEST_PASSWORD = "password123"

def test_calendar_view_toggle():
    """Test the calendar view toggle functionality"""
    
    print("🧪 Testing Stylist Calendar View Toggle Feature")
    print("=" * 50)
    
    # Test 1: Personal View (default)
    print("\n1. Testing Personal View (default)...")
    personal_url = f"{BASE_URL}/appointments/stylist-appointments?calendar_view=personal"
    response = requests.get(personal_url)
    
    if response.status_code == 200:
        print("✅ Personal view accessible")
        if "My Appointments" in response.text:
            print("✅ Personal view title correct")
        else:
            print("❌ Personal view title incorrect")
    else:
        print(f"❌ Personal view failed: {response.status_code}")
    
    # Test 2: Global View
    print("\n2. Testing Global View...")
    global_url = f"{BASE_URL}/appointments/stylist-appointments?calendar_view=global"
    response = requests.get(global_url)
    
    if response.status_code == 200:
        print("✅ Global view accessible")
        if "Salon Schedule" in response.text:
            print("✅ Global view title correct")
        else:
            print("❌ Global view title incorrect")
    else:
        print(f"❌ Global view failed: {response.status_code}")
    
    # Test 3: Toggle Controls
    print("\n3. Testing Toggle Controls...")
    response = requests.get(f"{BASE_URL}/appointments/stylist-appointments")
    
    if response.status_code == 200:
        if "calendar_view" in response.text and "Personal" in response.text and "Global Salon" in response.text:
            print("✅ Toggle controls present")
        else:
            print("❌ Toggle controls missing")
        
        # Check for auto-submit functionality
        if "auto-submit" in response.text:
            print("✅ Auto-submit functionality detected")
        else:
            print("❌ Auto-submit functionality missing")
            
        # Check for helpful hints
        if "click to switch" in response.text:
            print("✅ User hints present")
        else:
            print("❌ User hints missing")
    else:
        print(f"❌ Toggle controls test failed: {response.status_code}")
    
    # Test 4: URL Parameter Persistence
    print("\n4. Testing URL Parameter Persistence...")
    test_url = f"{BASE_URL}/appointments/stylist-appointments?calendar_view=global&view_type=week&date={date.today().isoformat()}"
    response = requests.get(test_url)
    
    if response.status_code == 200:
        if "calendar_view=global" in response.text:
            print("✅ URL parameters persist correctly")
        else:
            print("❌ URL parameters not persisting")
    else:
        print(f"❌ URL parameter test failed: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 Calendar View Toggle Test Complete!")

def test_api_endpoints():
    """Test the API endpoints for calendar data"""
    
    print("\n🔌 Testing API Endpoints")
    print("=" * 30)
    
    # Test appointments API
    api_url = f"{BASE_URL}/appointments/api/appointments"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        print("✅ Appointments API accessible")
        try:
            data = response.json()
            print(f"✅ API returned {len(data)} appointments")
        except json.JSONDecodeError:
            print("❌ API response not valid JSON")
    else:
        print(f"❌ Appointments API failed: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Starting Calendar View Toggle Tests")
    print(f"📍 Testing against: {BASE_URL}")
    
    try:
        test_calendar_view_toggle()
        test_api_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the application. Make sure it's running on http://localhost:5010")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    print("\n📋 Test Summary:")
    print("- Calendar view toggle should work for stylists")
    print("- Personal view shows only stylist's appointments")
    print("- Global view shows all salon appointments")
    print("- Toggle controls should be visible and functional")
    print("- URL parameters should persist across navigation") 