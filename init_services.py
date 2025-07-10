#!/usr/bin/env python3
"""
Initialize sample services and help set up stylist users for testing.
Run this script to add sample services to the database.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Service, User, Role
from app.extensions import db

def init_services():
    """Initialize sample services in the database."""
    app = create_app()
    
    with app.app_context():
        # Check if services already exist
        existing_services = Service.query.all()
        if existing_services:
            print(f"Found {len(existing_services)} existing services:")
            for service in existing_services:
                print(f"  - {service.name} (£{service.price}) - {service.duration}min")
            return
        
        # Create sample services
        services_data = [
            {
                'name': 'Haircut & Style',
                'description': 'Professional haircut with styling and blow-dry',
                'duration': 60,
                'price': 35.00,
                'is_active': True
            },
            {
                'name': 'Haircut Only',
                'description': 'Basic haircut service',
                'duration': 45,
                'price': 25.00,
                'is_active': True
            },
            {
                'name': 'Full Color',
                'description': 'Complete hair coloring service',
                'duration': 120,
                'price': 75.00,
                'is_active': True
            },
            {
                'name': 'Highlights',
                'description': 'Professional highlighting service',
                'duration': 90,
                'price': 65.00,
                'is_active': True
            },
            {
                'name': 'Blow Dry & Style',
                'description': 'Wash, blow dry and styling',
                'duration': 45,
                'price': 30.00,
                'is_active': True
            },
            {
                'name': 'Deep Conditioning Treatment',
                'description': 'Nourishing deep conditioning treatment',
                'duration': 30,
                'price': 25.00,
                'is_active': True
            },
            {
                'name': 'Updo/Special Occasion',
                'description': 'Special occasion styling and updo',
                'duration': 90,
                'price': 55.00,
                'is_active': True
            },
            {
                'name': 'Men\'s Haircut',
                'description': 'Professional men\'s haircut and styling',
                'duration': 30,
                'price': 20.00,
                'is_active': True
            }
        ]
        
        for service_data in services_data:
            service = Service(**service_data)
            db.session.add(service)
            print(f"Adding service: {service.name}")
        
        db.session.commit()
        print(f"\n✅ Successfully added {len(services_data)} services to the database!")

def check_stylists():
    """Check if there are any stylist users in the database."""
    app = create_app()
    
    with app.app_context():
        stylist_role = Role.query.filter_by(name='stylist').first()
        if not stylist_role:
            print("❌ No 'stylist' role found in the database!")
            return
        
        stylists = User.query.join(User.roles).filter(
            User.is_active == True,
            User.roles.contains(stylist_role)
        ).all()
        
        if stylists:
            print(f"✅ Found {len(stylists)} stylist(s):")
            for stylist in stylists:
                print(f"  - {stylist.first_name} {stylist.last_name} ({stylist.email})")
        else:
            print("❌ No stylist users found!")
            print("\nTo create a stylist user:")
            print("1. Register a new user account")
            print("2. Go to Admin panel (if you're a manager/owner)")
            print("3. Assign the 'stylist' role to the user")
            print("\nOr create a stylist directly in the database.")

def main():
    print("Salon ESE - Service Initialization")
    print("=" * 40)
    
    # Initialize services
    print("\n1. Initializing services...")
    init_services()
    
    # Check stylists
    print("\n2. Checking stylist users...")
    check_stylists()
    
    print("\n" + "=" * 40)
    print("Setup complete!")
    print("\nNext steps:")
    print("- Create stylist users if none exist")
    print("- Test the booking system with a customer account")
    print("- Make sure stylists have the 'stylist' role assigned")

if __name__ == '__main__':
    main() 