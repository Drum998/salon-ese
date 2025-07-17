#!/usr/bin/env python3
"""
Migration script for new salon management models
This script creates the new tables and initializes default data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import (
    SalonSettings, WorkPattern, EmploymentDetails, 
    HolidayQuota, HolidayRequest, BillingElement
)

def migrate_new_models():
    """Create new tables and initialize default data"""
    app = create_app()
    
    with app.app_context():
        print("Starting migration for new salon management models...")
        
        try:
            # Create all tables (this will create the new ones)
            db.create_all()
            print("✓ All tables created successfully")
            
            # Initialize default salon settings
            print("Initializing default salon settings...")
            settings = SalonSettings.query.first()
            if not settings:
                default_hours = {
                    'monday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'tuesday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'wednesday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'thursday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'friday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'saturday': {'open': '09:00', 'close': '17:00', 'closed': False},
                    'sunday': {'open': '10:00', 'close': '16:00', 'closed': True}
                }
                settings = SalonSettings(
                    salon_name='Salon ESE',
                    opening_hours=default_hours,
                    emergency_extension_enabled=True
                )
                db.session.add(settings)
                print("✓ Default salon settings created")
            
            # Initialize default billing elements
            print("Initializing default billing elements...")
            default_elements = [
                {'name': 'Color', 'percentage': 25.00},
                {'name': 'Electric', 'percentage': 15.00},
                {'name': 'Products', 'percentage': 10.00},
                {'name': 'Equipment', 'percentage': 5.00},
                {'name': 'Overheads', 'percentage': 20.00}
            ]
            
            for element_data in default_elements:
                element = BillingElement.query.filter_by(name=element_data['name']).first()
                if not element:
                    element = BillingElement(**element_data)
                    db.session.add(element)
                    print(f"✓ Added billing element: {element_data['name']} ({element_data['percentage']}%)")
            
            # Commit all changes
            db.session.commit()
            print("✓ Migration completed successfully!")
            
            # Print summary
            print("\nMigration Summary:")
            print(f"- Salon Settings: {SalonSettings.query.count()} record(s)")
            print(f"- Billing Elements: {BillingElement.query.count()} record(s)")
            print(f"- Total percentage of billing elements: {BillingElement.get_total_percentage()}%")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_new_models() 