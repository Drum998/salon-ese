#!/usr/bin/env python3
"""
Simple database test script to verify models and connection work correctly.
Run this script to test the database setup without the full Flask application.
"""

import os
import sys
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
        
        # Test creating a role
        print("Testing role creation...")
        test_role = Role(name='test_role', description='Test role')
        session.add(test_role)
        session.commit()
        print("✓ Role created successfully")
        
        # Test creating a user
        print("Testing user creation...")
        test_user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        test_user.set_password('password123')
        session.add(test_user)
        session.commit()
        print("✓ User created successfully")
        
        # Test querying
        print("Testing queries...")
        user = session.query(User).filter_by(username='testuser').first()
        role = session.query(Role).filter_by(name='test_role').first()
        print(f"✓ Found user: {user.username}")
        print(f"✓ Found role: {role.name}")
        
        # Clean up
        session.delete(user)
        session.delete(role)
        session.commit()
        print("✓ Cleanup completed")
        
        session.close()
        print("✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_database_connection()
    sys.exit(0 if success else 1) 