#!/usr/bin/env python3
"""
Simple database test script to verify models and connection work correctly.
Run this script to test the database setup without the full Flask application.
"""

import os
import sys
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Role, UserProfile, LoginAttempt
from app.extensions import db
from config import Config

def test_database_connection():
    """Test database connection and model creation."""
    print("Testing database connection...")
    
    # Set up database URL
    if os.environ.get('DOCKER_ENV'):
        database_url = 'postgresql://salon_user:salon_password@db:5432/salon_ese'
    else:
        database_url = 'sqlite:///test.db'
    
    print(f"Using database URL: {database_url}")
    
    try:
        # Create engine and session
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test creating tables
        print("Creating tables...")
        db.metadata.create_all(engine)
        print("✓ Tables created successfully")
        
        # Generate unique test data to avoid conflicts
        unique_suffix = str(uuid.uuid4())[:8]
        test_role_name = f'test_role_{unique_suffix}'
        test_username = f'testuser_{unique_suffix}'
        test_email = f'test_{unique_suffix}@example.com'
        
        # Test creating a role
        print("Testing role creation...")
        test_role = Role(name=test_role_name, description='Test role')
        session.add(test_role)
        session.commit()
        print("✓ Role created successfully")
        
        # Test creating a user
        print("Testing user creation...")
        test_user = User(
            username=test_username,
            email=test_email,
            first_name='Test',
            last_name='User'
        )
        test_user.set_password('password123')
        session.add(test_user)
        session.commit()
        print("✓ User created successfully")
        
        # Test querying
        print("Testing queries...")
        user = session.query(User).filter_by(username=test_username).first()
        role = session.query(Role).filter_by(name=test_role_name).first()
        print(f"✓ Found user: {user.username}")
        print(f"✓ Found role: {role.name}")
        
        # Assert that we found the expected data
        assert user is not None, "User should be found"
        assert role is not None, "Role should be found"
        assert user.username == test_username, "Username should match"
        assert role.name == test_role_name, "Role name should match"
        
        # Clean up
        session.delete(user)
        session.delete(role)
        session.commit()
        print("✓ Cleanup completed")
        
        session.close()
        print("✓ All tests passed!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    test_database_connection() 