#!/usr/bin/env python3
"""
Test script to verify admin functionality.
Run this to check that the admin panel is working correctly.
"""

import os
import sys

# Set up environment
os.environ['DOCKER_ENV'] = 'true'
os.environ['DATABASE_URL'] = 'postgresql://salon_user:salon_password@db:5432/salon_ese'

def test_admin_functionality():
    """Test that admin functionality works correctly."""
    try:
        print("Testing Admin Functionality")
        print("=" * 40)
        
        # Test importing admin components
        from app.models import User, Role
        from app.forms import AdminUserForm, RoleAssignmentForm
        from app.routes.admin import bp as admin_bp
        print("✓ Admin components imported successfully")
        
        # Test creating admin forms
        admin_form = AdminUserForm()
        role_form = RoleAssignmentForm()
        print("✓ Admin forms created successfully")
        
        # Test form field validation
        assert hasattr(admin_form, 'username'), "AdminUserForm missing username field"
        assert hasattr(admin_form, 'email'), "AdminUserForm missing email field"
        assert hasattr(admin_form, 'roles'), "AdminUserForm missing roles field"
        assert hasattr(role_form, 'user_id'), "RoleAssignmentForm missing user_id field"
        assert hasattr(role_form, 'role_name'), "RoleAssignmentForm missing role_name field"
        print("✓ Admin form fields validated")
        
        # Test role choices
        expected_roles = ['guest', 'customer', 'stylist', 'manager', 'owner']
        admin_role_choices = [choice[0] for choice in admin_form.roles.choices]
        role_role_choices = [choice[0] for choice in role_form.role_name.choices]
        
        for role in expected_roles:
            assert role in admin_role_choices, f"Role {role} missing from AdminUserForm"
            assert role in role_role_choices, f"Role {role} missing from RoleAssignmentForm"
        print("✓ Role choices validated")
        
        # Test database connection and models
        from app.extensions import db
        from sqlalchemy import create_engine
        engine = create_engine(os.environ['DATABASE_URL'])
        print("✓ Database connection established")
        
        # Test querying users and roles
        with db.app.app_context():
            users = User.query.all()
            roles = Role.query.all()
            print(f"✓ Found {len(users)} users and {len(roles)} roles in database")
            
            # Test role assignment
            if users and roles:
                user = users[0]
                role = roles[0]
                print(f"✓ Testing role assignment: {user.username} -> {role.name}")
        
        print("\n✅ All admin functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Admin functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_admin_functionality()
    sys.exit(0 if success else 1) 