#!/usr/bin/env python3
"""
Simple test script to verify models can be imported and relationships work.
"""

import os
import sys

# Set up environment
os.environ['DOCKER_ENV'] = 'true'
os.environ['DATABASE_URL'] = 'postgresql://salon_user:salon_password@db:5432/salon_ese'

def test_models():
    """Test that models can be imported and relationships are valid."""
    try:
        print("Testing model imports...")
        
        # Test importing models
        from app.models import User, Role, UserProfile, LoginAttempt, user_roles
        print("✓ All models imported successfully")
        
        # Test creating SQLAlchemy engine
        from sqlalchemy import create_engine
        engine = create_engine(os.environ['DATABASE_URL'])
        print("✓ Database engine created successfully")
        
        # Test creating tables
        from app.extensions import db
        db.metadata.create_all(engine)
        print("✓ Tables created successfully")
        
        # Test relationship inspection
        print("Testing relationship inspection...")
        user_roles_rel = User.__mapper__.relationships['roles']
        print(f"✓ User.roles relationship: {user_roles_rel}")
        
        print("✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_models()
    sys.exit(0 if success else 1) 