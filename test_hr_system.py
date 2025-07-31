#!/usr/bin/env python3
"""
HR System Test Script
Tests all HR system functionality including cost calculations, employment details, and financial tracking
"""

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, Role, EmploymentDetails, Appointment, AppointmentCost, Service
from app.services.hr_service import HRService

def test_hr_system():
    """Test the HR system functionality"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing HR System Integration")
        print("=" * 50)
        
        # Test 1: Employment Details Model
        print("\n1. Testing Employment Details Model...")
        test_employment_details_model()
        
        # Test 2: HR Service Functions
        print("\n2. Testing HR Service Functions...")
        test_hr_service_functions()
        
        # Test 3: Cost Calculations
        print("\n3. Testing Cost Calculations...")
        test_cost_calculations()
        
        # Test 4: Financial Reports
        print("\n4. Testing Financial Reports...")
        test_financial_reports()
        
        # Test 5: Employment Summary
        print("\n5. Testing Employment Summary...")
        test_employment_summary()
        
        print("\n✅ All HR System Tests Completed!")

def test_employment_details_model():
    """Test employment details model functionality"""
    try:
        # Get a stylist user
        stylist_role = Role.query.filter_by(name='stylist').first()
        if not stylist_role:
            print("❌ No stylist role found")
            return
        
        stylist = User.query.join(User.roles).filter(Role.name == 'stylist').first()
        if not stylist:
            print("❌ No stylist users found")
            return
        
        # Test employment details creation
        employment = EmploymentDetails.query.filter_by(user_id=stylist.id).first()
        if not employment:
            print("❌ No employment details found for stylist")
            return
        
        # Test model methods
        print(f"✓ Employment type: {employment.employment_type}")
        print(f"✓ Is employed: {employment.is_employed}")
        print(f"✓ Is self-employed: {employment.is_self_employed}")
        print(f"✓ Currently employed: {employment.is_currently_employed()}")
        print(f"✓ Current rate: {employment.get_current_rate()}")
        
        # Test cost calculations
        if employment.is_employed and employment.hourly_rate:
            cost = employment.calculate_hourly_cost(2.5)
            print(f"✓ Hourly cost for 2.5 hours: £{cost:.2f}")
        
        if employment.is_self_employed and employment.commission_rate:
            cost = employment.calculate_commission_cost(100.0)
            print(f"✓ Commission cost for £100: £{cost:.2f}")
        
        print("✅ Employment Details Model Test Passed")
        
    except Exception as e:
        print(f"❌ Employment Details Model Test Failed: {str(e)}")

def test_hr_service_functions():
    """Test HR service functions"""
    try:
        # Test employment summary
        summary = HRService.get_employment_summary()
        print(f"✓ Employment summary: {summary['total_stylists']} stylists")
        print(f"✓ Employed: {summary['employed_count']}, Self-employed: {summary['self_employed_count']}")
        print(f"✓ Active: {summary['active_count']}, Inactive: {summary['inactive_count']}")
        
        # Test salon profit calculation
        profit = HRService.calculate_salon_profit()
        print(f"✓ Salon profit: £{profit['total_profit']:.2f}")
        print(f"✓ Total revenue: £{profit['total_revenue']:.2f}")
        print(f"✓ Profit margin: {profit['profit_margin']:.1f}%")
        
        # Test stylist earnings
        stylists = User.query.join(User.roles).filter(Role.name == 'stylist').limit(3).all()
        for stylist in stylists:
            earnings = HRService.calculate_stylist_earnings(stylist.id)
            print(f"✓ {stylist.first_name} earnings: £{earnings['total_earnings']:.2f}")
        
        print("✅ HR Service Functions Test Passed")
        
    except Exception as e:
        print(f"❌ HR Service Functions Test Failed: {str(e)}")

def test_cost_calculations():
    """Test appointment cost calculations"""
    try:
        # Get completed appointments
        appointments = Appointment.query.filter_by(status='completed').limit(5).all()
        
        if not appointments:
            print("⚠️  No completed appointments found for cost calculation testing")
            return
        
        print(f"Testing cost calculations for {len(appointments)} appointments...")
        
        for appointment in appointments:
            # Calculate cost
            cost_record = HRService.calculate_appointment_cost(appointment.id)
            
            if cost_record:
                print(f"✓ Appointment {appointment.id}:")
                print(f"  - Revenue: £{cost_record.service_revenue:.2f}")
                print(f"  - Stylist Cost: £{cost_record.stylist_cost:.2f}")
                print(f"  - Salon Profit: £{cost_record.salon_profit:.2f}")
                print(f"  - Method: {cost_record.calculation_method}")
                print(f"  - Margin: {cost_record.profit_margin_percentage:.1f}%")
            else:
                print(f"⚠️  No cost record for appointment {appointment.id}")
        
        print("✅ Cost Calculations Test Passed")
        
    except Exception as e:
        print(f"❌ Cost Calculations Test Failed: {str(e)}")

def test_financial_reports():
    """Test financial reporting functionality"""
    try:
        # Test date range filtering
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        # Test salon profit with date range
        profit = HRService.calculate_salon_profit(start_date, end_date)
        print(f"✓ Salon profit (last 30 days): £{profit['total_profit']:.2f}")
        
        # Test stylist earnings with date range
        stylists = User.query.join(User.roles).filter(Role.name == 'stylist').limit(2).all()
        for stylist in stylists:
            earnings = HRService.calculate_stylist_earnings(stylist.id, start_date, end_date)
            print(f"✓ {stylist.first_name} earnings (last 30 days): £{earnings['total_earnings']:.2f}")
        
        # Test stylist performance report
        if stylists:
            performance = HRService.get_stylist_performance_report(stylists[0].id, start_date, end_date)
            if performance:
                print(f"✓ Performance report for {performance['stylist_name']}:")
                print(f"  - Total appointments: {performance['total_appointments']}")
                print(f"  - Completion rate: {performance['completion_rate']:.1f}%")
                print(f"  - Total earnings: £{performance['earnings']['total_earnings']:.2f}")
        
        print("✅ Financial Reports Test Passed")
        
    except Exception as e:
        print(f"❌ Financial Reports Test Failed: {str(e)}")

def test_employment_summary():
    """Test employment summary functionality"""
    try:
        summary = HRService.get_employment_summary()
        
        print("Employment Summary:")
        print(f"✓ Total stylists: {summary['total_stylists']}")
        print(f"✓ Employed: {summary['employed_count']}")
        print(f"✓ Self-employed: {summary['self_employed_count']}")
        print(f"✓ Active: {summary['active_count']}")
        print(f"✓ Inactive: {summary['inactive_count']}")
        print(f"✓ Monthly base cost: £{summary['total_monthly_cost']:.2f}")
        
        print("\nEmployment Details:")
        for detail in summary['employment_details'][:3]:  # Show first 3
            print(f"✓ {detail['name']}: {detail['employment_type']} - {detail['job_role'] or 'N/A'}")
        
        print("✅ Employment Summary Test Passed")
        
    except Exception as e:
        print(f"❌ Employment Summary Test Failed: {str(e)}")

def create_test_data():
    """Create test data for HR system testing"""
    app = create_app()
    
    with app.app_context():
        print("Creating test data for HR system...")
        
        # Create test employment details if none exist
        stylists = User.query.join(User.roles).filter(Role.name == 'stylist').all()
        
        for stylist in stylists:
            existing = EmploymentDetails.query.filter_by(user_id=stylist.id).first()
            if not existing:
                # Create employment details
                employment = EmploymentDetails(
                    user_id=stylist.id,
                    employment_type='employed' if stylist.id % 2 == 0 else 'self_employed',
                    start_date=date.today() - timedelta(days=365),
                    hourly_rate=Decimal('15.00') if stylist.id % 2 == 0 else None,
                    commission_rate=Decimal('70.00') if stylist.id % 2 == 1 else None,
                    base_salary=Decimal('2000.00') if stylist.id % 2 == 0 else None,
                    billing_method='salon_bills',
                    job_role='Senior Stylist' if stylist.id % 2 == 0 else 'Self-Employed Stylist'
                )
                db.session.add(employment)
        
        db.session.commit()
        print("✅ Test data created")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'create-data':
        create_test_data()
    else:
        test_hr_system() 