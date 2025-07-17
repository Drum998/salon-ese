#!/usr/bin/env python3
"""
Test script for new salon management models
This script tests the functionality of all new models
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import (
    User, Role, SalonSettings, WorkPattern, EmploymentDetails, 
    HolidayQuota, HolidayRequest, BillingElement
)
from datetime import date, datetime, time

def test_new_models():
    """Test all new models and their functionality"""
    app = create_app()
    
    with app.app_context():
        print("Testing new salon management models...")
        
        try:
            # Test 1: SalonSettings
            print("\n1. Testing SalonSettings...")
            settings = SalonSettings.get_settings()
            print(f"✓ Salon name: {settings.salon_name}")
            print(f"✓ Emergency extension enabled: {settings.emergency_extension_enabled}")
            print(f"✓ Monday hours: {settings.opening_hours['monday']}")
            
            # Test 2: BillingElement
            print("\n2. Testing BillingElement...")
            elements = BillingElement.get_active_elements()
            print(f"✓ Active billing elements: {len(elements)}")
            total_percentage = BillingElement.get_total_percentage()
            print(f"✓ Total percentage: {total_percentage}%")
            
            for element in elements:
                print(f"  - {element.name}: {element.percentage}%")
            
            # Test 3: WorkPattern
            print("\n3. Testing WorkPattern...")
            # Create a test user first
            test_user = User.query.filter_by(username='test_stylist').first()
            if not test_user:
                # Create a test user
                test_user = User(
                    username='test_stylist',
                    email='test@example.com',
                    first_name='Test',
                    last_name='Stylist'
                )
                test_user.set_password('password123')
                db.session.add(test_user)
                db.session.commit()
                print("✓ Created test user")
            
            # Create a work pattern
            work_schedule = {
                'monday': {'working': True, 'start_time': '09:00', 'end_time': '17:00'},
                'tuesday': {'working': True, 'start_time': '09:00', 'end_time': '17:00'},
                'wednesday': {'working': True, 'start_time': '09:00', 'end_time': '17:00'},
                'thursday': {'working': True, 'start_time': '09:00', 'end_time': '17:00'},
                'friday': {'working': True, 'start_time': '09:00', 'end_time': '17:00'},
                'saturday': {'working': False, 'start_time': '09:00', 'end_time': '17:00'},
                'sunday': {'working': False, 'start_time': '10:00', 'end_time': '16:00'}
            }
            
            work_pattern = WorkPattern.query.filter_by(user_id=test_user.id).first()
            if not work_pattern:
                work_pattern = WorkPattern(
                    user_id=test_user.id,
                    pattern_name='Full Time Weekdays',
                    work_schedule=work_schedule
                )
                db.session.add(work_pattern)
                db.session.commit()
                print("✓ Created work pattern")
            
            weekly_hours = work_pattern.get_weekly_hours()
            print(f"✓ Weekly hours: {weekly_hours}")
            
            # Test 4: EmploymentDetails
            print("\n4. Testing EmploymentDetails...")
            emp_details = EmploymentDetails.query.filter_by(user_id=test_user.id).first()
            if not emp_details:
                emp_details = EmploymentDetails(
                    user_id=test_user.id,
                    employment_type='employed',
                    billing_method='salon_bills',
                    job_role='Senior Stylist'
                )
                db.session.add(emp_details)
                db.session.commit()
                print("✓ Created employment details")
            
            print(f"✓ Employment type: {emp_details.employment_type}")
            print(f"✓ Billing method: {emp_details.billing_method}")
            print(f"✓ Job role: {emp_details.job_role}")
            print(f"✓ Is self-employed: {emp_details.is_self_employed}")
            
            # Test 5: HolidayQuota
            print("\n5. Testing HolidayQuota...")
            current_year = date.today().year
            quota = HolidayQuota.query.filter_by(
                user_id=test_user.id, 
                year=current_year
            ).first()
            
            if not quota:
                entitled_days = HolidayQuota.calculate_entitlement(weekly_hours)
                quota = HolidayQuota(
                    user_id=test_user.id,
                    year=current_year,
                    total_hours_per_week=weekly_hours,
                    holiday_days_entitled=entitled_days,
                    holiday_days_remaining=entitled_days
                )
                db.session.add(quota)
                db.session.commit()
                print("✓ Created holiday quota")
            
            print(f"✓ Holiday days entitled: {quota.holiday_days_entitled}")
            print(f"✓ Holiday days taken: {quota.holiday_days_taken}")
            print(f"✓ Holiday days remaining: {quota.holiday_days_remaining}")
            
            # Test 6: HolidayRequest
            print("\n6. Testing HolidayRequest...")
            holiday_request = HolidayRequest(
                user_id=test_user.id,
                start_date=date(current_year, 7, 15),
                end_date=date(current_year, 7, 19),
                days_requested=5,
                notes='Summer holiday'
            )
            db.session.add(holiday_request)
            db.session.commit()
            print("✓ Created holiday request")
            
            print(f"✓ Holiday request status: {holiday_request.status}")
            print(f"✓ Days requested: {holiday_request.days_requested}")
            print(f"✓ Is pending: {holiday_request.is_pending}")
            
            # Test 7: Holiday approval process
            print("\n7. Testing holiday approval process...")
            # Get a manager user for approval
            manager_role = Role.query.filter_by(name='manager').first()
            if manager_role and manager_role.users.first():
                manager = manager_role.users.first()
                holiday_request.approve(manager)
                db.session.commit()
                print("✓ Holiday request approved")
                print(f"✓ New status: {holiday_request.status}")
                print(f"✓ Approved by: {holiday_request.approved_by.username}")
                
                # Check updated quota
                quota.refresh()
                print(f"✓ Updated holiday days taken: {quota.holiday_days_taken}")
                print(f"✓ Updated holiday days remaining: {quota.holiday_days_remaining}")
            else:
                print("⚠ No manager found for approval test")
            
            print("\n✓ All model tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    test_new_models() 