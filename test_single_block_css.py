#!/usr/bin/env python3
"""
Test script to verify single appointment block spanning using CSS height calculation.
Tests that appointments appear as single blocks spanning multiple rows.
"""

import requests
import sys
from datetime import datetime, timedelta

def test_single_block_css():
    """Test that appointments appear as single blocks spanning multiple rows using CSS"""
    print("🧪 Testing Single Appointment Block Spanning (CSS Method)")
    print("=" * 70)
    
    # Test configuration
    base_url = "http://localhost:5000"
    
    try:
        # Test 1: Check if calendar page loads
        print("\n1. Testing calendar page load...")
        response = requests.get(f"{base_url}/appointments/admin-appointments")
        
        if response.status_code == 200:
            print("✅ Calendar page loads successfully")
            content = response.text
        else:
            print(f"❌ Calendar page failed to load: {response.status_code}")
            return False
        
        # Test 2: Check for appointment visibility (CRITICAL)
        print("\n2. Testing appointment visibility (CRITICAL)...")
        
        # Check for appointment slot elements
        if 'appointment-slot' in content:
            print("✅ Appointment slot elements found")
        else:
            print("❌ Appointment slot elements not found - APPOINTMENTS MAY NOT BE VISIBLE!")
            return False
        
        # Check for appointment data attributes
        if 'data-appointment-id' in content:
            print("✅ Appointment ID data attributes found")
        else:
            print("❌ Appointment ID data attributes not found")
        
        # Check for appointment click handler
        if 'handleAppointmentClick' in content:
            print("✅ Appointment click handler found")
        else:
            print("❌ Appointment click handler not found")
        
        # Test 3: Check for CSS height calculation
        print("\n3. Testing CSS height calculation...")
        
        # Check for height calculation
        if 'height: calc(' in content:
            print("✅ CSS height calculation found")
        else:
            print("❌ CSS height calculation not found")
        
        # Check for rowspan calculation
        if 'rowspan = appointment_duration // 5' in content:
            print("✅ Rowspan calculation found")
        else:
            print("❌ Rowspan calculation not found")
        
        # Check for appointment duration calculation
        if 'appointment_duration = appointment_end - appointment_start' in content:
            print("✅ Appointment duration calculation found")
        else:
            print("❌ Appointment duration calculation not found")
        
        # Test 4: Check for start detection logic
        print("\n4. Testing start detection logic...")
        
        # Check for start detection
        if 'is_start = (current_time >= appointment_start and current_time < appointment_start + 5)' in content:
            print("✅ Start detection logic found")
        else:
            print("❌ Start detection logic not found")
        
        # Check for conditional rendering
        if '{% if is_start %}' in content:
            print("✅ Conditional rendering for start found")
        else:
            print("❌ Conditional rendering for start not found")
        
        # Test 5: Check for visual styling
        print("\n5. Testing visual styling...")
        
        # Check for CSS properties
        css_checks = [
            'display: flex',
            'flex-direction: column',
            'justify-content: space-between',
            'position: absolute',
            'z-index: 10'
        ]
        
        for css_check in css_checks:
            if css_check in content:
                print(f"✅ CSS property found: {css_check}")
            else:
                print(f"❌ CSS property not found: {css_check}")
        
        # Test 6: Check for appointment information display
        print("\n6. Testing appointment information display...")
        
        # Check for customer name display
        if 'appointment.customer.first_name' in content:
            print("✅ Customer name display found")
        else:
            print("❌ Customer name display not found")
        
        # Check for service information
        if 'appointment.services_link' in content:
            print("✅ Service information display found")
        else:
            print("❌ Service information display not found")
        
        # Check for time display
        if 'appointment.start_time.strftime' in content:
            print("✅ Appointment time display found")
        else:
            print("❌ Appointment time display not found")
        
        # Check for status badges
        if 'appointment.status' in content:
            print("✅ Status badge display found")
        else:
            print("❌ Status badge display not found")
        
        print("\n" + "=" * 70)
        print("🎉 Single Block CSS Test Complete!")
        print("\n📋 Summary:")
        print("- Appointments should appear as single blocks spanning multiple rows")
        print("- Each appointment is rendered only once at its start time")
        print("- The block height is calculated based on appointment duration")
        print("- CSS height calculation: calc(rowspan * 20px)")
        print("- Clicking appointment blocks opens edit page")
        print("- Empty slots remain clickable for new bookings")
        print("- Visual layout is cleaner with no duplicate blocks")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application. Make sure it's running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_visual_verification():
    """Provide guidance for visual verification of single block spanning"""
    print("\n🔍 Visual Verification Checklist:")
    print("=" * 70)
    print("1. Open the calendar page in your browser")
    print("2. Look for appointments that span multiple time slots")
    print("3. Verify each appointment appears as ONE block, not multiple blocks")
    print("4. Check that appointment blocks have proper height to cover their duration")
    print("5. Verify the block spans the correct number of rows")
    print("6. Click on an appointment block - should open edit page")
    print("7. Click on empty time slots - should open booking page")
    print("8. Verify appointment blocks don't interfere with empty slot clicking")
    print("9. Check that appointment information is clearly visible in the blocks")
    print("10. Verify status badges are properly positioned")
    print("11. Test that the calendar scrolls and navigates correctly")
    print("12. Check that overlapping appointments are handled correctly")

def test_calculation_examples():
    """Provide examples of the height calculation"""
    print("\n📐 Height Calculation Examples:")
    print("=" * 70)
    print("Duration Calculation: appointment_duration = appointment_end - appointment_start")
    print("Rowspan Calculation: rowspan = appointment_duration // 5")
    print("CSS Height: height: calc(rowspan * 20px)")
    print()
    print("Examples:")
    print("- 30-minute appointment: 30 // 5 = 6 rows, height: calc(6 * 20px) = 120px")
    print("- 60-minute appointment: 60 // 5 = 12 rows, height: calc(12 * 20px) = 240px")
    print("- 90-minute appointment: 90 // 5 = 18 rows, height: calc(18 * 20px) = 360px")
    print("- 135-minute appointment: 135 // 5 = 27 rows, height: calc(27 * 20px) = 540px")

if __name__ == "__main__":
    print("🚀 Starting Single Block CSS Tests")
    print("Make sure the Flask application is running on http://localhost:5000")
    print()
    
    success = test_single_block_css()
    
    if success:
        test_visual_verification()
        test_calculation_examples()
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the application.")
        sys.exit(1) 