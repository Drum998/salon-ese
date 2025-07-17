#!/usr/bin/env python3
"""
Debug script to understand form validation issues
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Role, EmploymentDetails, SalonSettings, WorkPattern
from app.forms import EmploymentDetailsForm, SalonSettingsForm, WorkPatternForm

def init_database():
    """Initialize database with roles"""
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Database initialization attempt {attempt}/{max_attempts}")
            db.create_all()
            print("✓ Tables created successfully")
            
            # Create roles if they don't exist
            roles = ['guest', 'customer', 'stylist', 'manager', 'owner']
            for role_name in roles:
                role = Role.query.filter_by(name=role_name).first()
                if not role:
                    role = Role(name=role_name)
                    db.session.add(role)
                    print(f"✓ Added role: {role_name}")
                else:
                    print(f"✓ Role already exists: {role_name}")
            
            db.session.commit()
            print("✓ Database initialization completed successfully")
            return True
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_attempts:
                db.session.rollback()
            else:
                print("Failed to initialize database after all attempts")
                return False

def debug_employment_details_form():
    """Debug employment details form validation"""
    app = create_app('testing')
    
    with app.app_context():
        # Initialize database
        if not init_database():
            return
        
        # Query for roles (do not create duplicates)
        stylist_role = Role.query.filter_by(name='stylist').first()
        
        # Create a test user
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        user.roles.append(stylist_role)
        db.session.add(user)
        db.session.commit()
        
        # Create employment details
        details = EmploymentDetails(
            user_id=user.id,
            employment_type='employed',
            billing_method='salon_bills',
            job_role='Stylist'
        )
        db.session.add(details)
        db.session.commit()
        
        print(f"Created employment details with ID: {details.id}")
        print(f"Original employment_type: {details.employment_type}")
        
        # Test form with edit data - simulate POST request
        form_data = {
            'user_id': str(user.id),
            'employment_type': 'self_employed',
            'commission_percentage': '75.00',
            'billing_method': 'stylist_bills',
            'job_role': 'Updated Freelance Stylist'
        }
        
        # Create a test request context with POST data
        with app.test_request_context('/', method='POST', data=form_data):
            form = EmploymentDetailsForm()  # Don't pass employment_details to avoid overwriting POST data
            
            print(f"Form is_submitted(): {form.is_submitted()}")
            print(f"Form validate(): {form.validate()}")
            print(f"Form validate_on_submit(): {form.validate_on_submit()}")
            print(f"Form errors: {form.errors}")
            
            if form.validate_on_submit():
                print("Form would update successfully")
                details.user_id = form.user_id.data
                details.employment_type = form.employment_type.data
                details.commission_percentage = float(form.commission_percentage.data) if form.commission_percentage.data else None
                details.billing_method = form.billing_method.data
                details.job_role = form.job_role.data
                
                db.session.commit()
                print(f"Updated employment_type: {details.employment_type}")
            else:
                print("Form validation failed")

def debug_salon_settings_form():
    """Debug salon settings form validation"""
    app = create_app('testing')
    
    with app.app_context():
        # Initialize database
        if not init_database():
            return
        
        # Get or create salon settings
        settings = SalonSettings.get_settings()
        print(f"Original salon_name: {settings.salon_name}")
        
        # Test form with update data - simulate POST request
        form_data = {
            'salon_name': 'Updated Salon Name',
            'emergency_extension_enabled': 'on',  # Use 'on' for boolean fields
            'monday_open': '10:00',
            'monday_close': '19:00',
            'monday_closed': '',  # Empty string for unchecked boolean
            'tuesday_open': '10:00',
            'tuesday_close': '19:00',
            'tuesday_closed': '',
            'wednesday_open': '10:00',
            'wednesday_close': '19:00',
            'wednesday_closed': '',
            'thursday_open': '10:00',
            'thursday_close': '19:00',
            'thursday_closed': '',
            'friday_open': '10:00',
            'friday_close': '19:00',
            'friday_closed': '',
            'saturday_open': '09:00',
            'saturday_close': '17:00',
            'saturday_closed': '',
            'sunday_open': '09:00',
            'sunday_close': '17:00',
            'sunday_closed': 'on'  # Use 'on' for checked boolean
        }
        
        # Create a test request context with POST data
        with app.test_request_context('/', method='POST', data=form_data):
            form = SalonSettingsForm()  # Don't pass salon_settings to avoid overwriting POST data
            
            print(f"Form is_submitted(): {form.is_submitted()}")
            print(f"Form validate(): {form.validate()}")
            print(f"Form validate_on_submit(): {form.validate_on_submit()}")
            print(f"Form errors: {form.errors}")
            
            if form.validate_on_submit():
                print("Form would update successfully")
                settings.salon_name = form.salon_name.data
                settings.emergency_extension_enabled = form.emergency_extension_enabled.data
                settings.opening_hours = form.get_opening_hours_dict()
                
                db.session.commit()
                print(f"Updated salon_name: {settings.salon_name}")
            else:
                print("Form validation failed")

def debug_work_pattern_form():
    """Debug work pattern form validation"""
    app = create_app('testing')
    
    with app.app_context():
        # Initialize database
        if not init_database():
            return
        
        # Query for roles (do not create duplicates)
        stylist_role = Role.query.filter_by(name='stylist').first()
        manager_role = Role.query.filter_by(name='manager').first()
        
        # Create a test user
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        user.roles.append(stylist_role)
        db.session.add(user)
        db.session.commit()
        
        # Create work pattern
        work_schedule = {
            'monday': {'working': True, 'start': '09:00', 'end': '17:00'},
            'tuesday': {'working': True, 'start': '09:00', 'end': '17:00'},
            'wednesday': {'working': True, 'start': '09:00', 'end': '17:00'},
            'thursday': {'working': True, 'start': '09:00', 'end': '17:00'},
            'friday': {'working': True, 'start': '09:00', 'end': '17:00'},
            'saturday': {'working': False, 'start': None, 'end': None},
            'sunday': {'working': False, 'start': None, 'end': None}
        }
        
        pattern = WorkPattern(
            user_id=user.id,
            pattern_name='Original Pattern',
            work_schedule=work_schedule,
            is_active=True
        )
        db.session.add(pattern)
        db.session.commit()
        
        print(f"Created work pattern with ID: {pattern.id}")
        print(f"Original pattern_name: {pattern.pattern_name}")
        
        # Test form with edit data - simulate POST request
        form_data = {
            'user_id': user.id,
            'pattern_name': 'Updated Pattern',
            'is_active': 'on',  # Use 'on' for boolean fields
            'monday_start': '10:00',
            'monday_end': '18:00',
            'monday_working': 'on',
            'tuesday_start': '10:00',
            'tuesday_end': '18:00',
            'tuesday_working': 'on',
            'wednesday_start': '10:00',
            'wednesday_end': '18:00',
            'wednesday_working': 'on',
            'thursday_start': '10:00',
            'thursday_end': '18:00',
            'thursday_working': 'on',
            'friday_start': '10:00',
            'friday_end': '18:00',
            'friday_working': 'on',
            'saturday_start': '',
            'saturday_end': '',
            'saturday_working': '',  # Empty string for unchecked boolean
            'sunday_start': '',
            'sunday_end': '',
            'sunday_working': ''  # Empty string for unchecked boolean
        }
        
        # Create a test request context with POST data
        with app.test_request_context('/', method='POST', data=form_data):
            form = WorkPatternForm()  # Don't pass work_pattern to avoid overwriting POST data
            
            print(f"Form is_submitted(): {form.is_submitted()}")
            print(f"Form validate(): {form.validate()}")
            print(f"Form validate_on_submit(): {form.validate_on_submit()}")
            print(f"Form errors: {form.errors}")
            
            if form.validate_on_submit():
                print("Form would update successfully")
                pattern.user_id = form.user_id.data
                pattern.pattern_name = form.pattern_name.data
                pattern.work_schedule = form.get_work_schedule_dict()
                pattern.is_active = form.is_active.data
                
                db.session.commit()
                print(f"Updated pattern_name: {pattern.pattern_name}")
            else:
                print("Form validation failed")

if __name__ == '__main__':
    print("=== Debugging Employment Details Form ===")
    debug_employment_details_form()
    print("\n=== Debugging Salon Settings Form ===")
    debug_salon_settings_form()
    print("\n=== Debugging Work Pattern Form ===")
    debug_work_pattern_form() 