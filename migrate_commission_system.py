#!/usr/bin/env python3
"""
Migration script for Commission Calculation System
Adds new commission-related fields to AppointmentCost model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import AppointmentCost, EmploymentDetails, BillingElement
from decimal import Decimal
import json

def migrate_commission_system():
    """Migrate database for commission calculation system"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting Commission System Migration...")
        
        # Check if new columns already exist
        inspector = db.inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('appointment_cost')]
        
        new_columns = [
            'commission_breakdown',
            'billing_method', 
            'billing_elements_applied'
        ]
        
        # Add new columns if they don't exist
        for column in new_columns:
            if column not in existing_columns:
                print(f"📝 Adding column: {column}")
                
                if column == 'commission_breakdown':
                    db.engine.execute("ALTER TABLE appointment_cost ADD COLUMN commission_breakdown JSON")
                elif column == 'billing_method':
                    db.engine.execute("ALTER TABLE appointment_cost ADD COLUMN billing_method VARCHAR(20)")
                elif column == 'billing_elements_applied':
                    db.engine.execute("ALTER TABLE appointment_cost ADD COLUMN billing_elements_applied JSON")
            else:
                print(f"✅ Column {column} already exists")
        
        # Initialize billing elements if they don't exist
        print("📝 Initializing billing elements...")
        billing_elements = [
            {'name': 'Color', 'percentage': Decimal('25.00')},
            {'name': 'Electric', 'percentage': Decimal('15.00')},
            {'name': 'Styling', 'percentage': Decimal('20.00')},
            {'name': 'Treatment', 'percentage': Decimal('10.00')},
            {'name': 'Other', 'percentage': Decimal('30.00')}
        ]
        
        for element_data in billing_elements:
            existing = BillingElement.query.filter_by(name=element_data['name']).first()
            if not existing:
                element = BillingElement(
                    name=element_data['name'],
                    percentage=element_data['percentage']
                )
                db.session.add(element)
                print(f"✅ Added billing element: {element_data['name']}")
        
        # Update existing appointment costs with billing method
        print("📝 Updating existing appointment costs...")
        appointment_costs = AppointmentCost.query.all()
        
        for cost in appointment_costs:
            # Get employment details to determine billing method
            employment = EmploymentDetails.query.filter_by(user_id=cost.stylist_id).first()
            if employment:
                cost.billing_method = employment.billing_method
                
                # Create basic commission breakdown for existing records
                if cost.calculation_method == 'commission' and cost.commission_amount:
                    breakdown = {
                        'total_commission': float(cost.commission_amount),
                        'commission_percentage': float(employment.commission_rate) if employment.commission_rate else 0,
                        'service_revenue': float(cost.service_revenue),
                        'calculation_method': 'percentage'
                    }
                    cost.commission_breakdown = breakdown
                    
                    # Apply default billing elements
                    billing_elements = BillingElement.get_active_elements()
                    elements_applied = {}
                    for element in billing_elements:
                        elements_applied[element.name] = {
                            'percentage': float(element.percentage),
                            'amount': float(cost.service_revenue) * (float(element.percentage) / 100)
                        }
                    cost.billing_elements_applied = elements_applied
        
        db.session.commit()
        print("✅ Commission system migration completed successfully!")
        
        # Print summary
        total_costs = AppointmentCost.query.count()
        updated_costs = AppointmentCost.query.filter(AppointmentCost.billing_method.isnot(None)).count()
        billing_elements_count = BillingElement.query.count()
        
        print(f"\n📊 Migration Summary:")
        print(f"   - Total appointment costs: {total_costs}")
        print(f"   - Updated appointment costs: {updated_costs}")
        print(f"   - Billing elements created: {billing_elements_count}")
        print(f"   - New columns added: {len([col for col in new_columns if col not in existing_columns])}")

if __name__ == '__main__':
    migrate_commission_system() 