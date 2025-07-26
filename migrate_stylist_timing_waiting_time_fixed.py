#!/usr/bin/env python3
"""
Fixed migration script to add custom_waiting_time column to StylistServiceTiming table
This version checks if the column exists before trying to add it.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db

def migrate_stylist_timing_waiting_time():
    """Add custom_waiting_time column to StylistServiceTiming table if it doesn't exist"""
    app = create_app()
    
    with app.app_context():
        print("Starting StylistServiceTiming custom_waiting_time migration...")
        
        try:
            # Check if the column already exists
            print("Checking if custom_waiting_time column exists...")
            result = db.engine.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'stylist_service_timing' AND column_name = 'custom_waiting_time'
            """).fetchone()
            
            if result:
                print("✓ custom_waiting_time column already exists - skipping migration!")
                print("Migration completed successfully!")
                return True
            
            # Add the new column if it doesn't exist
            print("Adding custom_waiting_time column...")
            db.engine.execute("""
                ALTER TABLE stylist_service_timing 
                ADD COLUMN custom_waiting_time INTEGER
            """)
            print("✓ custom_waiting_time column added successfully!")
            
            # Verify the column exists
            result = db.engine.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'stylist_service_timing' AND column_name = 'custom_waiting_time'
            """).fetchone()
            
            if result:
                print("✓ Column verification successful!")
            else:
                print("⚠ Warning: Column verification failed!")
            
            print("\nMigration completed successfully!")
            print("\nNext steps:")
            print("1. Test the stylist timing form to ensure custom waiting time works")
            print("2. Verify that existing stylist timings still work correctly")
            print("3. Test booking appointments with custom waiting times")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
        
        return True

if __name__ == '__main__':
    success = migrate_stylist_timing_waiting_time()
    sys.exit(0 if success else 1) 