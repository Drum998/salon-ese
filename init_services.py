#!/usr/bin/env python3
"""
Initialize sample services for the salon appointment system.
Run this script after setting up the database to add some default services.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import Service

def init_services():
    """Initialize sample services in the database."""
    app = create_app()
    
    with app.app_context():
        # Check if services already exist
        existing_services = Service.query.count()
        if existing_services > 0:
            print(f"Found {existing_services} existing services. Skipping initialization.")
            return
        
        # Sample services
        services = [
            {
                'name': 'Haircut & Style',
                'description': 'Professional haircut with styling and blow-dry',
                'duration': 60,
                'price': 45.00,
                'is_active': True
            },
            {
                'name': 'Hair Coloring',
                'description': 'Full hair coloring service with consultation',
                'duration': 120,
                'price': 85.00,
                'is_active': True
            },
            {
                'name': 'Highlights',
                'description': 'Professional highlights with foil technique',
                'duration': 90,
                'price': 75.00,
                'is_active': True
            },
            {
                'name': 'Hair Treatment',
                'description': 'Deep conditioning treatment for damaged hair',
                'duration': 45,
                'price': 35.00,
                'is_active': True
            },
            {
                'name': 'Updo & Styling',
                'description': 'Special occasion styling and updo',
                'duration': 75,
                'price': 55.00,
                'is_active': True
            },
            {
                'name': 'Men\'s Haircut',
                'description': 'Classic men\'s haircut and styling',
                'duration': 45,
                'price': 30.00,
                'is_active': True
            },
            {
                'name': 'Children\'s Haircut',
                'description': 'Haircut for children under 12',
                'duration': 30,
                'price': 25.00,
                'is_active': True
            },
            {
                'name': 'Consultation',
                'description': 'Hair consultation and style advice',
                'duration': 30,
                'price': 20.00,
                'is_active': True
            }
        ]
        
        # Add services to database
        for service_data in services:
            service = Service(**service_data)
            db.session.add(service)
            print(f"Added service: {service.name}")
        
        db.session.commit()
        print(f"Successfully initialized {len(services)} services!")

if __name__ == '__main__':
    init_services() 