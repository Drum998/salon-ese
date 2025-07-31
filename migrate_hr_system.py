#!/usr/bin/env python3
"""
HR System Migration Script
Adds new HR fields to employment_details table and creates appointment_cost table
"""

import os
import sys
from datetime import datetime, date
from decimal import Decimal

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import EmploymentDetails, Appointment, AppointmentCost, User, Service
from app.services.hr_service import HRService

def migrate_hr_system():
    """Migrate the database to add HR system fields"""
    app = create_app()
    
    with app.app_context():
        print("Starting HR System Migration...")
        
        try:
            # Check if new columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('employment_details')]
            
            new_columns = ['start_date', 'end_date', 'hourly_rate', 'commission_rate', 'base_salary']
            missing_columns = [col for col in new_columns if col not in existing_columns]
            
            if missing_columns:
                print(f"Adding missing columns: {missing_columns}")
                
                # Add new columns to employment_details table
                for column in missing_columns:
                    if column == 'start_date':
                        db.engine.execute("ALTER TABLE employment_details ADD COLUMN start_date DATE NOT NULL DEFAULT CURRENT_DATE")
                    elif column == 'end_date':
                        db.engine.execute("ALTER TABLE employment_details ADD COLUMN end_date DATE")
                    elif column == 'hourly_rate':
                        db.engine.execute("ALTER TABLE employment_details ADD COLUMN hourly_rate NUMERIC(8,2)")
                    elif column == 'commission_rate':
                        db.engine.execute("ALTER TABLE employment_details ADD COLUMN commission_rate NUMERIC(5,2)")
                    elif column == 'base_salary':
                        db.engine.execute("ALTER TABLE employment_details ADD COLUMN base_salary NUMERIC(10,2)")
                
                print("✓ Added new columns to employment_details table")
            else:
                print("✓ All HR columns already exist in employment_details table")
            
            # Check if appointment_cost table exists
            if not inspector.has_table('appointment_cost'):
                print("Creating appointment_cost table...")
                
                # Create appointment_cost table
                db.engine.execute("""
                    CREATE TABLE appointment_cost (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        appointment_id INTEGER NOT NULL,
                        stylist_id INTEGER NOT NULL,
                        service_revenue NUMERIC(10,2) NOT NULL,
                        stylist_cost NUMERIC(10,2) NOT NULL,
                        salon_profit NUMERIC(10,2) NOT NULL,
                        calculation_method VARCHAR(20) NOT NULL,
                        hours_worked NUMERIC(4,2),
                        commission_amount NUMERIC(10,2),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (appointment_id) REFERENCES appointment (id),
                        FOREIGN KEY (stylist_id) REFERENCES user (id)
                    )
                """)
                
                print("✓ Created appointment_cost table")
            else:
                print("✓ appointment_cost table already exists")
            
            # Update existing employment details with default values
            print("Updating existing employment details...")
            existing_details = EmploymentDetails.query.all()
            
            for detail in existing_details:
                updated = False
                
                # Set default start date if not set
                if not hasattr(detail, 'start_date') or not detail.start_date:
                    detail.start_date = date.today()
                    updated = True
                
                # Set commission_rate from commission_percentage if not set
                if hasattr(detail, 'commission_rate') and not detail.commission_rate and detail.commission_percentage:
                    detail.commission_rate = detail.commission_percentage
                    updated = True
                
                if updated:
                    db.session.add(detail)
            
            db.session.commit()
            print("✓ Updated existing employment details")
            
            # Calculate costs for existing appointments
            print("Calculating costs for existing appointments...")
            appointments = Appointment.query.filter_by(status='completed').all()
            
            cost_count = 0
            for appointment in appointments:
                # Check if cost record already exists
                existing_cost = AppointmentCost.query.filter_by(appointment_id=appointment.id).first()
                if not existing_cost:
                    # Calculate cost
                    cost_record = HRService.calculate_appointment_cost(appointment.id)
                    if cost_record:
                        cost_count += 1
            
            print(f"✓ Calculated costs for {cost_count} appointments")
            
            print("\n🎉 HR System Migration Completed Successfully!")
            print("\nSummary:")
            print(f"- Added {len(missing_columns)} new columns to employment_details table")
            print(f"- Updated {len(existing_details)} existing employment records")
            print(f"- Calculated costs for {cost_count} existing appointments")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            raise

def test_hr_system():
    """Test the HR system functionality"""
    app = create_app()
    
    with app.app_context():
        print("\nTesting HR System...")
        
        # Test employment summary
        try:
            summary = HRService.get_employment_summary()
            print(f"✓ Employment summary: {summary['total_stylists']} stylists")
        except Exception as e:
            print(f"❌ Employment summary failed: {str(e)}")
        
        # Test salon profit calculation
        try:
            profit = HRService.calculate_salon_profit()
            print(f"✓ Salon profit calculation: £{profit['total_profit']:.2f}")
        except Exception as e:
            print(f"❌ Salon profit calculation failed: {str(e)}")
        
        # Test stylist earnings calculation
        try:
            stylists = User.query.join(User.roles).filter(User.roles.any(name='stylist')).limit(1).all()
            if stylists:
                earnings = HRService.calculate_stylist_earnings(stylists[0].id)
                print(f"✓ Stylist earnings calculation: £{earnings['total_earnings']:.2f}")
        except Exception as e:
            print(f"❌ Stylist earnings calculation failed: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_hr_system()
    else:
        migrate_hr_system() 