#!/usr/bin/env python3
"""
Migration script for StylistServiceAssociation model
Run this script to add the stylist-service association table to the database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import StylistServiceAssociation

def migrate_stylist_service_associations():
    """Add StylistServiceAssociation table to the database"""
    app = create_app()
    
    with app.app_context():
        print("Starting StylistServiceAssociation migration...")
        
        try:
            # Create the new table
            print("Creating StylistServiceAssociation table...")
            db.create_all()
            print("✓ StylistServiceAssociation table created successfully!")
            
            # Verify the table exists (works with both SQLite and PostgreSQL)
            try:
                # Try PostgreSQL syntax first
                result = db.engine.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'stylist_service_association'
                """).fetchone()
            except:
                # Fall back to SQLite syntax
                result = db.engine.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='stylist_service_association'
                """).fetchone()
            
            if result:
                print("✓ Table verification successful!")
            else:
                print("⚠ Warning: Table verification failed!")
            
            print("\nMigration completed successfully!")
            print("\nNext steps:")
            print("1. Access the Stylist-Service Associations management page")
            print("2. Create associations to restrict which stylists can perform which services")
            print("3. Test the booking system to ensure restrictions are working")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
        
        return True

if __name__ == '__main__':
    success = migrate_stylist_service_associations()
    sys.exit(0 if success else 1) 