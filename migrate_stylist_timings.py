#!/usr/bin/env python3
"""
Migration script to add StylistServiceTiming table and waiting_time field to Service table.
Run this script to update the database schema for enhanced service management.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import StylistServiceTiming, Service
from sqlalchemy import inspect

def table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_stylist_timings():
    """Migrate database to add StylistServiceTiming table and waiting_time field"""
    app = create_app()
    
    with app.app_context():
        print("Starting migration for stylist service timings...")
        
        try:
            # Create StylistServiceTiming table if it doesn't exist
            if not table_exists('stylist_service_timing'):
                print("Creating StylistServiceTiming table...")
                StylistServiceTiming.__table__.create(db.engine)
                print("✓ StylistServiceTiming table created")
            else:
                print("StylistServiceTiming table already exists")
            
            # Check if waiting_time column exists in Service table
            if not column_exists('service', 'waiting_time'):
                print("Adding waiting_time column to Service table...")
                db.engine.execute('ALTER TABLE service ADD COLUMN waiting_time INTEGER')
                print("✓ waiting_time column added to Service table")
            else:
                print("waiting_time column already exists in Service table")
            
            print("✓ Migration completed successfully!")
            print("\nNext steps:")
            print("1. Rebuild your Docker container to apply the changes")
            print("2. Access the 'Stylist Timings' page from the navigation menu")
            print("3. Add custom timing for stylists who complete services faster/slower")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_stylist_timings() 