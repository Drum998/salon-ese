#!/usr/bin/env python3
"""
Debug script to test form validation and identify issues.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, Role, EmploymentDetails
from app.forms import EmploymentDetailsForm

def test_form_validation():
    """Test form validation in isolation."""
    print("🧪 Testing Form Validation")
    print("=" * 40)
    
    # Create test app
    app = create_app('testing')
    
    with app.app_context():
        # Create database
        db.create_all()
        
        # Create test roles
        roles = ['guest', 'customer', 'stylist', 'manager', 'owner']
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=f'Test {role_name} role')
                db.session.add(role)
        
        db.session.commit()
        
        # Create test user
        stylist_role = Role.query.filter_by(name='stylist').first()
        user = User(
            username='test_stylist',
            email='test@example.com',
            first_name='Test',
            last_name='Stylist',
            is_active=True,
            email_verified=True
        )
        user.set_password('password123')
        user.roles.append(stylist_role)
        db.session.add(user)
        db.session.commit()
        
        print(f"✓ Created test user: {user.username}")
        print(f"✓ User ID: {user.id}")
        print(f"✓ User roles: {[r.name for r in user.roles]}")
        
        # Test form validation
        print("\n📋 Testing EmploymentDetailsForm validation...")
        
        # Test valid employed form
        form_data = {
            'user_id': user.id,
            'employment_type': 'employed',
            'commission_percentage': '',
            'billing_method': 'salon_bills',
            'job_role': 'Senior Stylist'
        }
        
        form = EmploymentDetailsForm(data=form_data)
        print(f"✓ Form created successfully")
        print(f"✓ Form user_id choices: {form.user_id.choices}")
        
        is_valid = form.validate()
        print(f"✓ Form validation result: {is_valid}")
        
        if not is_valid:
            print(f"✗ Form errors: {form.errors}")
        
        # Test valid self-employed form
        form_data2 = {
            'user_id': user.id,
            'employment_type': 'self_employed',
            'commission_percentage': '70.00',
            'billing_method': 'stylist_bills',
            'job_role': 'Freelance Stylist'
        }
        
        form2 = EmploymentDetailsForm(data=form_data2)
        is_valid2 = form2.validate()
        print(f"✓ Self-employed form validation result: {is_valid2}")
        
        if not is_valid2:
            print(f"✗ Self-employed form errors: {form2.errors}")
        
        # Test commission validation for employed
        form_data3 = {
            'user_id': user.id,
            'employment_type': 'employed',
            'commission_percentage': '70.00',  # Should fail
            'billing_method': 'salon_bills',
            'job_role': 'Stylist'
        }
        
        form3 = EmploymentDetailsForm(data=form_data3)
        is_valid3 = form3.validate()
        print(f"✓ Employed with commission validation result: {is_valid3}")
        
        if not is_valid3:
            print(f"✗ Employed with commission errors: {form3.errors}")
        
        print("\n✅ Form validation tests completed!")

if __name__ == '__main__':
    test_form_validation() 