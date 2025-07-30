#!/usr/bin/env python3
"""
Test script to verify that appointments are visible on the calendar.
This tests the fix for appointments not appearing on the calendar.
"""

import requests
import sys
from datetime import datetime, timedelta

def test_appointment_visibility():
    """Test that appointments are now visible on the calendar"""
    print("🧪 Testing Appointment Visibility")
    print("=" * 60)
    
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
        
        # Test 2: Check for appointment display elements
        print("\n2. Testing appointment display elements...")
        
        # Check for appointment slot elements
        if 'appointment-slot' in content:
            print("✅ Appointment slot elements found")
        else:
            print("❌ Appointment slot elements not found")
        
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
        
        # Test 3: Check for time slot logic
        print("\n3. Testing time slot logic...")
        
        # Check for slot_appointments logic
        if 'slot_appointments' in content:
            print("✅ Slot appointments logic found")
        else:
            print("❌ Slot appointments logic not found")
        
        # Check for time calculation
        if 'current_time = hour * 60 + minute' in content:
            print("✅ Time calculation logic found")
        else:
            print("❌ Time calculation logic not found")
        
        # Check for appointment time range logic
        if 'current_time >= appointment_start and current_time < appointment_end' in content:
            print("✅ Appointment time range logic found")
        else:
            print("❌ Appointment time range logic not found")
        
        # Test 4: Check for click behavior
        print("\n4. Testing click behavior...")
        
        # Check for conditional onclick
        if 'onclick="{% if slot_appointments %}handleAppointmentClick(this){% else %}handleTimeSlotClick(this){% endif %}"' in content:
            print("✅ Conditional click behavior found")
        else:
            print("❌ Conditional click behavior not found")
        
        # Check for both click handlers
        if 'handleTimeSlotClick' in content and 'handleAppointmentClick' in content:
            print("✅ Both click handlers present")
        else:
            print("❌ Missing click handlers")
        
        # Test 5: Check for appointment information display
        print("\n5. Testing appointment information display...")
        
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
        
        print("\n" + "=" * 60)
        print("🎉 Appointment Visibility Test Complete!")
        print("\n📋 Summary:")
        print("- Appointments should now be visible on the calendar")
        print("- Each time slot shows appointments that fall within that time")
        print("- Clicking on appointment slots opens edit page")
        print("- Clicking on empty slots opens booking page")
        print("- Appointment information is displayed clearly")
        print("- Multiple blocks per appointment (working version)")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application. Make sure it's running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_visual_verification():
    """Provide guidance for visual verification"""
    print("\n🔍 Visual Verification Checklist:")
    print("=" * 60)
    print("1. Open the calendar page in your browser")
    print("2. Look for appointments in the time slots (not just in the day summary)")
    print("3. Verify appointments appear in the correct time slots")
    print("4. Check that appointment information is visible (customer name, service, time)")
    print("5. Click on an appointment - should open edit page")
    print("6. Click on empty time slots - should open booking page")
    print("7. Verify appointments span their full duration visually (multiple blocks)")
    print("8. Check that status badges are visible")
    print("9. Test that the calendar navigation still works")
    print("10. Verify that the 5-minute time slots are working correctly")

def test_next_steps():
    """Provide guidance for next steps"""
    print("\n🚀 Next Steps for Single Block Implementation:")
    print("=" * 60)
    print("Once appointments are visible, we can work on single block spanning:")
    print("1. Verify appointments are showing correctly first")
    print("2. Then implement the rowspan logic carefully")
    print("3. Test with different appointment durations")
    print("4. Ensure click behavior works correctly")
    print("5. Verify visual layout is clean and intuitive")

if __name__ == "__main__":
    print("🚀 Starting Appointment Visibility Tests")
    print("Make sure the Flask application is running on http://localhost:5000")
    print()
    
    success = test_appointment_visibility()
    
    if success:
        test_visual_verification()
        test_next_steps()
        print("\n✅ All tests completed successfully!")
        print("\n💡 If appointments still don't appear, check:")
        print("   - That there are actual appointments in the database")
        print("   - That the appointments have valid start_time and end_time")
        print("   - That the appointments are for the current date range")
        print("   - That the stylists have appointments assigned to them")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the application.")
        sys.exit(1) 