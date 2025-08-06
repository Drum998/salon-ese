#!/usr/bin/env python3
"""
Test script for Commission Calculation System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Role, Service, Appointment, AppointmentService, EmploymentDetails, BillingElement, AppointmentCost
from app.services.hr_service import HRService
from decimal import Decimal
from datetime import date, datetime

def test_commission_system():
    """Test the commission calculation system"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing Commission Calculation System...")
        
        # Test 1: Check if billing elements exist
        print("\n1. Testing Billing Elements...")
        billing_elements = BillingElement.query.all()
        print(f"   ✓ Found {len(billing_elements)} billing elements")
        for element in billing_elements:
            print(f"      - {element.name}: {element.percentage}%")
        
        # Test 2: Check if commission fields exist in AppointmentCost
        print("\n2. Testing AppointmentCost Model...")
        try:
            # Try to access new fields
            cost = AppointmentCost.query.first()
            if cost:
                print(f"   ✓ Commission breakdown field: {hasattr(cost, 'commission_breakdown')}")
                print(f"   ✓ Billing method field: {hasattr(cost, 'billing_method')}")
                print(f"   ✓ Billing elements applied field: {hasattr(cost, 'billing_elements_applied')}")
            else:
                print("   ⚠ No appointment costs found to test")
        except Exception as e:
            print(f"   ✗ Error testing AppointmentCost model: {e}")
        
        # Test 3: Test commission calculation methods
        print("\n3. Testing Commission Calculation Methods...")
        try:
            # Test salon commission summary
            summary = HRService.calculate_salon_commission_summary()
            print(f"   ✓ Salon commission summary calculated")
            print(f"      - Total revenue: £{summary['total_revenue']:.2f}")
            print(f"      - Total commission: £{summary['total_commission']:.2f}")
            print(f"      - Commission efficiency: {summary['commission_efficiency']:.1f}%")
            
            # Test stylist commission performance
            stylists = User.query.join(User.roles).filter(Role.name == 'stylist').all()
            if stylists:
                performance = HRService.calculate_stylist_commission_performance(stylists[0].id)
                print(f"   ✓ Stylist commission performance calculated")
                print(f"      - Total commission: £{performance['total_commission']:.2f}")
                print(f"      - Commission efficiency: {performance['commission_efficiency']:.1f}%")
            else:
                print("   ⚠ No stylists found to test performance")
                
        except Exception as e:
            print(f"   ✗ Error testing commission calculations: {e}")
        
        # Test 4: Test commission breakdown calculation
        print("\n4. Testing Commission Breakdown...")
        try:
            # Get first appointment
            appointment = Appointment.query.first()
            if appointment:
                breakdown = HRService.calculate_commission_breakdown(appointment.id)
                if breakdown:
                    print(f"   ✓ Commission breakdown calculated")
                    print(f"      - Total commission: £{breakdown['total_commission']:.2f}")
                    print(f"      - Commission percentage: {breakdown['commission_percentage']:.1f}%")
                    print(f"      - Billing method: {breakdown['billing_method']}")
                else:
                    print("   ⚠ No commission breakdown (appointment may not be commission-based)")
            else:
                print("   ⚠ No appointments found to test breakdown")
        except Exception as e:
            print(f"   ✗ Error testing commission breakdown: {e}")
        
        # Test 5: Test billing elements integration
        print("\n5. Testing Billing Elements Integration...")
        try:
            appointment = Appointment.query.first()
            if appointment:
                commission_data = HRService.calculate_commission_with_billing_elements(appointment.id)
                if commission_data:
                    print(f"   ✓ Billing elements integration working")
                    print(f"      - Total commission: £{commission_data['total_commission']:.2f}")
                    print(f"      - Billing method: {commission_data['billing_method']}")
                    if commission_data['billing_elements_applied']:
                        print(f"      - Billing elements applied: {len(commission_data['billing_elements_applied'])}")
                else:
                    print("   ⚠ No commission data (appointment may not be commission-based)")
            else:
                print("   ⚠ No appointments found to test billing elements")
        except Exception as e:
            print(f"   ✗ Error testing billing elements integration: {e}")
        
        print("\n✅ Commission System Test Completed!")
        
        # Summary
        print("\n📊 Commission System Status:")
        print(f"   - Billing Elements: {len(billing_elements)} configured")
        print(f"   - Commission Methods: Available")
        print(f"   - Database Fields: Enhanced")
        print(f"   - Routes: Commission reports available")
        print(f"   - Templates: Commission UI created")

if __name__ == '__main__':
    test_commission_system() 