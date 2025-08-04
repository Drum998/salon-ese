#!/usr/bin/env python3
"""
Migration script for Salon Hours Integration
This script initializes salon settings and ensures proper integration with the appointment system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import SalonSettings, User, Role
from datetime import datetime

def migrate_salon_hours_integration():
    """Initialize salon settings and ensure proper integration"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting Salon Hours Integration Migration...")
        
        # Check if salon settings already exist
        existing_settings = SalonSettings.query.first()
        
        if existing_settings:
            print("✅ Salon settings already exist")
            print(f"   Salon Name: {existing_settings.salon_name}")
            print(f"   Emergency Extensions: {'Enabled' if existing_settings.emergency_extension_enabled else 'Disabled'}")
            
            # Update existing settings if needed
            if not existing_settings.opening_hours:
                print("🔄 Updating existing settings with default opening hours...")
                existing_settings.opening_hours = {
                    'monday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'tuesday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'wednesday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'thursday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'friday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'saturday': {'open': '09:00', 'close': '17:00', 'closed': False},
                    'sunday': {'open': '10:00', 'close': '16:00', 'closed': True}
                }
                db.session.commit()
                print("✅ Opening hours updated")
        else:
            print("🔄 Creating default salon settings...")
            
            # Create default salon settings
            default_settings = SalonSettings(
                salon_name="Salon ESE",
                opening_hours={
                    'monday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'tuesday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'wednesday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'thursday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'friday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'saturday': {'open': '09:00', 'close': '17:00', 'closed': False},
                    'sunday': {'open': '10:00', 'close': '16:00', 'closed': True}
                },
                emergency_extension_enabled=True
            )
            
            db.session.add(default_settings)
            db.session.commit()
            print("✅ Default salon settings created")
        
        # Verify the integration service works
        print("🔄 Testing salon hours service...")
        try:
            from app.services.salon_hours_service import SalonHoursService
            
            # Test getting salon settings
            settings = SalonHoursService.get_salon_settings()
            print(f"✅ Salon settings retrieved: {settings.salon_name}")
            
            # Test getting opening hours for today
            today = datetime.now().date()
            hours = SalonHoursService.get_opening_hours_for_date(today)
            if hours:
                print(f"✅ Opening hours for today: {hours['open']} - {hours['close']}")
            else:
                print("⚠️  Salon is closed today")
            
            # Test generating time slots
            slots = SalonHoursService.generate_available_time_slots(today)
            print(f"✅ Generated {len(slots)} available time slots for today")
            
        except Exception as e:
            print(f"❌ Error testing salon hours service: {e}")
            return False
        
        print("✅ Salon Hours Integration Migration completed successfully!")
        return True

if __name__ == '__main__':
    success = migrate_salon_hours_integration()
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Start the application: docker-compose up -d")
        print("2. Access the admin panel and configure salon settings")
        print("3. Test appointment booking with salon hours integration")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1) 