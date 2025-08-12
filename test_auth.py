#!/usr/bin/env python3
"""
Authentication test script for Salon ESE
Tests user authentication, password hashing, and login functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Role
from werkzeug.security import check_password_hash
from datetime import datetime

def test_authentication():
    """Test authentication functionality"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing Authentication System...")
        
        # Test 1: User creation and password hashing
        print("\n1. Testing User Creation and Password Hashing...")
        try:
            # Create a test user
            test_user = User(
                username='test_auth_user',
                email='test_auth@example.com',
                first_name='Test',
                last_name='Auth'
            )
            test_user.set_password('testpassword123')
            
            # Test password hashing
            assert test_user.password_hash is not None, "Password should be hashed"
            assert test_user.password_hash != 'testpassword123', "Password should not be stored in plain text"
            assert check_password_hash(test_user.password_hash, 'testpassword123'), "Password verification should work"
            assert not check_password_hash(test_user.password_hash, 'wrongpassword'), "Wrong password should fail"
            
            print("✓ Password hashing and verification working correctly")
            
        except Exception as e:
            print(f"❌ Error testing password hashing: {e}")
            return
        
        # Test 2: User authentication
        print("\n2. Testing User Authentication...")
        try:
            # Test password verification
            assert test_user.check_password('testpassword123'), "Correct password should be accepted"
            assert not test_user.check_password('wrongpassword'), "Wrong password should be rejected"
            assert not test_user.check_password(''), "Empty password should be rejected"
            
            print("✓ User authentication working correctly")
            
        except Exception as e:
            print(f"❌ Error testing user authentication: {e}")
            return
        
        # Test 3: User properties
        print("\n3. Testing User Properties...")
        try:
            # Test user properties
            assert test_user.username == 'test_auth_user', "Username should match"
            assert test_user.email == 'test_auth@example.com', "Email should match"
            assert test_user.first_name == 'Test', "First name should match"
            assert test_user.last_name == 'Auth', "Last name should match"
            assert test_user.full_name == 'Test Auth', "Full name should be correct"
            
            print("✓ User properties working correctly")
            
        except Exception as e:
            print(f"❌ Error testing user properties: {e}")
            return
        
        # Test 4: User status
        print("\n4. Testing User Status...")
        try:
            # Test default status
            assert test_user.is_active, "New user should be active by default"
            assert not test_user.email_verified, "New user should not be email verified by default"
            
            # Test status changes
            test_user.is_active = False
            assert not test_user.is_active, "User should be deactivated"
            
            test_user.email_verified = True
            assert test_user.email_verified, "User should be email verified"
            
            print("✓ User status management working correctly")
            
        except Exception as e:
            print(f"❌ Error testing user status: {e}")
            return
        
        # Test 5: Role assignment
        print("\n5. Testing Role Assignment...")
        try:
            # Create a test role
            test_role = Role(
                name='test_auth_role',
                description='Test role for authentication'
            )
            
            # Assign role to user
            test_user.roles.append(test_role)
            assert test_role in test_user.roles, "Role should be assigned to user"
            assert test_user in test_role.users, "User should be in role's user list"
            
            print("✓ Role assignment working correctly")
            
        except Exception as e:
            print(f"❌ Error testing role assignment: {e}")
            return
        
        # Test 6: User serialization (for Flask-Login)
        print("\n6. Testing User Serialization...")
        try:
            # Test get_id method (required by Flask-Login)
            user_id = test_user.get_id()
            assert user_id == str(test_user.id), "User ID should be string representation"
            
            print("✓ User serialization working correctly")
            
        except Exception as e:
            print(f"❌ Error testing user serialization: {e}")
            return
        
        print("\n✅ All authentication tests passed!")
        
        # Clean up test data
        try:
            db.session.delete(test_user)
            db.session.delete(test_role)
            db.session.commit()
            print("✓ Test data cleaned up")
        except Exception as e:
            print(f"⚠ Warning: Could not clean up test data: {e}")

if __name__ == '__main__':
    test_authentication()
