#!/usr/bin/env python3
"""
Standalone test for salon settings functionality.
This can be run independently for smoke tests.
"""

import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_salon_settings_standalone():
    """Standalone test function for smoke tests."""
    try:
        from app import create_app
        from app.extensions import db
        from app.models import SalonSettings
        
        app = create_app()
        
        with app.app_context():
            print("🧪 Testing Salon Settings...")
            
            # Test 1: Get default settings
            print("\n1. Testing default settings retrieval...")
            settings = SalonSettings.get_settings()
            assert settings is not None, "Default settings should be created"
            assert settings.salon_name is not None, "Salon name should be set"
            print("✓ Default settings created successfully")
            
            # Test 2: Settings properties
            print("\n2. Testing settings properties...")
            assert hasattr(settings, 'salon_name'), "Settings should have salon_name"
            assert hasattr(settings, 'opening_hours'), "Settings should have opening_hours"
            assert hasattr(settings, 'emergency_extension_enabled'), "Settings should have emergency_extension_enabled"
            print("✓ Settings properties validated")
            
            # Test 3: Opening hours structure
            print("\n3. Testing opening hours structure...")
            assert isinstance(settings.opening_hours, dict), "Opening hours should be a dictionary"
            expected_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in expected_days:
                assert day in settings.opening_hours, f"Missing {day} in opening hours"
            print("✓ Opening hours structure validated")
            
            print("\n✅ All salon settings tests passed!")
            return True
            
    except Exception as e:
        print(f"\n❌ Salon settings test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_salon_settings_standalone()
    sys.exit(0 if success else 1) 