#!/usr/bin/env python3
"""
Enhanced script to add comprehensive test data across all systems:
- Users (manager, stylists, customers)
- Employment details with different types and commission rates
- Work patterns for stylists
- Holiday quotas and requests
- Appointments with costs and commission data
- Service associations and timings
- Billing elements and commission breakdowns

This creates a complete test environment to demonstrate all system features.
"""
from app import create_app
from app.extensions import db
from app.models import (
    User, Role, EmploymentDetails, WorkPattern, HolidayQuota, HolidayRequest,
    Appointment, AppointmentCost, AppointmentService, Service, StylistServiceAssociation,
    StylistServiceTiming, BillingElement, SalonSettings
)
from app.services.hr_service import HRService
from decimal import Decimal
from datetime import datetime, date, time, timedelta
import json
import random

def get_role(role_name):
    return Role.query.filter_by(name=role_name).first()

def add_user(username, email, first_name, last_name, password, roles):
    user = User.query.filter_by(username=username).first()
    if user:
        print(f"User {username} already exists.")
        return user
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=True
    )
    user.set_password(password)
    for role in roles:
        user.roles.append(role)
    db.session.add(user)
    print(f"Added user: {username} ({', '.join([r.name for r in roles])})")
    return user

def add_employment_details(user, employment_type, commission_rate=None, hourly_rate=None, base_salary=None):
    """Add employment details for a user"""
    existing = EmploymentDetails.query.filter_by(user_id=user.id).first()
    if existing:
        print(f"Employment details already exist for {user.username}")
        return existing
    
    employment = EmploymentDetails(
        user_id=user.id,
        employment_type=employment_type,
        commission_rate=commission_rate,
        hourly_rate=hourly_rate,
        base_salary=base_salary,
        billing_method='salon_bills' if employment_type == 'self_employed' else 'salon_bills',
        job_role='Senior Stylist' if employment_type == 'self_employed' else 'Junior Stylist',
        start_date=date.today() - timedelta(days=random.randint(30, 365))
    )
    db.session.add(employment)
    print(f"Added employment details for {user.username}: {employment_type}")
    return employment

def add_work_pattern(user, pattern_name, work_schedule):
    """Add work pattern for a user"""
    existing = WorkPattern.query.filter_by(user_id=user.id, pattern_name=pattern_name).first()
    if existing:
        print(f"Work pattern {pattern_name} already exists for {user.username}")
        return existing
    
    work_pattern = WorkPattern(
        user_id=user.id,
        pattern_name=pattern_name,
        work_schedule=work_schedule,
        is_active=True
    )
    db.session.add(work_pattern)
    print(f"Added work pattern '{pattern_name}' for {user.username}")
    return work_pattern

def add_holiday_quota(user, year, hours_per_week):
    """Add holiday quota for a user"""
    existing = HolidayQuota.query.filter_by(user_id=user.id, year=year).first()
    if existing:
        print(f"Holiday quota for {year} already exists for {user.username}")
        return existing
    
    entitlement = HolidayQuota.calculate_entitlement(hours_per_week)
    quota = HolidayQuota(
        user_id=user.id,
        year=year,
        total_hours_per_week=hours_per_week,
        holiday_days_entitled=entitlement,
        holiday_days_remaining=entitlement
    )
    db.session.add(quota)
    print(f"Added holiday quota for {user.username}: {entitlement} days")
    return quota

def add_holiday_request(user, start_date, end_date, status='approved'):
    """Add holiday request for a user"""
    request = HolidayRequest(
        user_id=user.id,
        start_date=start_date,
        end_date=end_date,
        days_requested=(end_date - start_date).days + 1,
        status=status,
        notes=f"Test holiday request for {user.username}"
    )
    if status == 'approved':
        request.approved_by_id = User.query.filter_by(username='manager_1').first().id
        request.approved_at = datetime.now()
    
    db.session.add(request)
    print(f"Added holiday request for {user.username}: {start_date} to {end_date} ({status})")
    return request

def add_service_association(stylist, service, is_allowed=True):
    """Add service association for a stylist"""
    existing = StylistServiceAssociation.query.filter_by(
        stylist_id=stylist.id, service_id=service.id
    ).first()
    if existing:
        print(f"Service association already exists for {stylist.username} - {service.name}")
        return existing
    
    association = StylistServiceAssociation(
        stylist_id=stylist.id,
        service_id=service.id,
        is_allowed=is_allowed,
        notes=f"Test association for {stylist.username}"
    )
    db.session.add(association)
    print(f"Added service association: {stylist.username} - {service.name}")
    return association

def add_stylist_timing(stylist, service, custom_duration=None, custom_waiting_time=None):
    """Add stylist-specific timing for a service"""
    existing = StylistServiceTiming.query.filter_by(
        stylist_id=stylist.id, service_id=service.id
    ).first()
    if existing:
        print(f"Stylist timing already exists for {stylist.username} - {service.name}")
        return existing
    
    timing = StylistServiceTiming(
        stylist_id=stylist.id,
        service_id=service.id,
        custom_duration=custom_duration or service.duration,
        custom_waiting_time=custom_waiting_time or service.waiting_time,
        notes=f"Custom timing for {stylist.username}"
    )
    db.session.add(timing)
    print(f"Added stylist timing: {stylist.username} - {service.name} ({timing.custom_duration}min)")
    return timing

def add_appointment(customer, stylist, service, appointment_date, start_time, status='confirmed'):
    """Add appointment with cost calculation"""
    # Create appointment
    appointment = Appointment(
        customer_id=customer.id,
        stylist_id=stylist.id,
        booked_by_id=customer.id,
        appointment_date=appointment_date,
        start_time=start_time,
        end_time=datetime.combine(appointment_date, start_time) + timedelta(minutes=service.duration),
        status=status,
        notes=f"Test appointment for {customer.username} with {stylist.username}"
    )
    db.session.add(appointment)
    db.session.flush()  # Get the appointment ID
    
    # Add service to appointment
    appointment_service = AppointmentService(
        appointment_id=appointment.id,
        service_id=service.id,
        duration=service.duration,
        waiting_time=service.waiting_time,
        order=1
    )
    db.session.add(appointment_service)
    
    # Calculate and add cost details
    employment = EmploymentDetails.query.filter_by(user_id=stylist.id).first()
    if employment:
        cost_data = HRService.calculate_appointment_cost(appointment.id)
        if cost_data:
            appointment_cost = AppointmentCost(
                appointment_id=appointment.id,
                stylist_id=stylist.id,
                service_revenue=service.price,
                stylist_cost=cost_data.get('stylist_cost', 0),
                salon_profit=cost_data.get('salon_profit', 0),
                calculation_method=cost_data.get('calculation_method', 'commission'),
                hours_worked=cost_data.get('hours_worked'),
                commission_amount=cost_data.get('commission_amount'),
                commission_breakdown=cost_data.get('commission_breakdown'),
                billing_method=cost_data.get('billing_method'),
                billing_elements_applied=cost_data.get('billing_elements_applied')
            )
            db.session.add(appointment_cost)
    
    print(f"Added appointment: {customer.username} with {stylist.username} - {service.name} on {appointment_date}")
    return appointment

def create_sample_data():
    """Create comprehensive sample data across all systems"""
    app = create_app()
    
    with app.app_context():
        print("🎯 Creating comprehensive test data...")
        
        # Get roles
        manager_role = get_role('manager')
        stylist_role = get_role('stylist')
        customer_role = get_role('customer')
        
        if not (manager_role and stylist_role and customer_role):
            print("❌ Required roles do not exist. Please ensure roles are seeded.")
            return
        
        # 1. Create Users
        print("\n👥 Creating users...")
        manager = add_user(
            username='manager_1',
            email='manager_1@example.com',
            first_name='Sarah',
            last_name='Manager',
            password='12345678',
            roles=[manager_role]
        )
        
        stylists = []
        for i in range(1, 4):
            stylist = add_user(
                username=f'stylist_{i}',
                email=f'stylist_{i}@example.com',
                first_name=f'Stylist{i}',
                last_name='Test',
                password='12345678',
                roles=[stylist_role]
            )
            stylists.append(stylist)
        
        customers = []
        for i in range(1, 6):
            customer = add_user(
                username=f'cust_{i}',
                email=f'cust_{i}@example.com',
                first_name=f'Customer{i}',
                last_name='Test',
                password='12345678',
                roles=[customer_role]
            )
            customers.append(customer)
        
        # 2. Create Employment Details
        print("\n💼 Creating employment details...")
        # Stylist 1: Self-employed with high commission
        add_employment_details(stylists[0], 'self_employed', commission_rate=Decimal('75.00'))
        
        # Stylist 2: Self-employed with medium commission
        add_employment_details(stylists[1], 'self_employed', commission_rate=Decimal('65.00'))
        
        # Stylist 3: Employed with hourly rate
        add_employment_details(stylists[2], 'employed', hourly_rate=Decimal('12.50'), base_salary=Decimal('20000.00'))
        
        # 3. Create Work Patterns
        print("\n📅 Creating work patterns...")
        standard_schedule = {
            'monday': {'start': '09:00', 'end': '17:00', 'working': True},
            'tuesday': {'start': '09:00', 'end': '17:00', 'working': True},
            'wednesday': {'start': '09:00', 'end': '17:00', 'working': True},
            'thursday': {'start': '09:00', 'end': '17:00', 'working': True},
            'friday': {'start': '09:00', 'end': '17:00', 'working': True},
            'saturday': {'start': '09:00', 'end': '16:00', 'working': True},
            'sunday': {'start': '09:00', 'end': '16:00', 'working': False}
        }
        
        part_time_schedule = {
            'monday': {'start': '10:00', 'end': '16:00', 'working': True},
            'tuesday': {'start': '10:00', 'end': '16:00', 'working': True},
            'wednesday': {'start': '10:00', 'end': '16:00', 'working': True},
            'thursday': {'start': '10:00', 'end': '16:00', 'working': True},
            'friday': {'start': '10:00', 'end': '16:00', 'working': True},
            'saturday': {'start': '09:00', 'end': '15:00', 'working': True},
            'sunday': {'start': '09:00', 'end': '15:00', 'working': False}
        }
        
        add_work_pattern(stylists[0], 'Full Time', standard_schedule)
        add_work_pattern(stylists[1], 'Full Time', standard_schedule)
        add_work_pattern(stylists[2], 'Part Time', part_time_schedule)
        
        # 4. Create Holiday Quotas and Requests
        print("\n🏖️ Creating holiday data...")
        current_year = date.today().year
        
        for stylist in stylists:
            add_holiday_quota(stylist, current_year, 40)
        
        # Add some holiday requests
        add_holiday_request(
            stylists[0], 
            date.today() + timedelta(days=30), 
            date.today() + timedelta(days=34), 
            'approved'
        )
        add_holiday_request(
            stylists[1], 
            date.today() + timedelta(days=60), 
            date.today() + timedelta(days=62), 
            'pending'
        )
        add_holiday_request(
            stylists[2], 
            date.today() + timedelta(days=90), 
            date.today() + timedelta(days=93), 
            'approved'
        )
        
        # 5. Get services and create associations
        print("\n🔗 Creating service associations...")
        services = Service.query.all()
        if not services:
            print("⚠️ No services found. Please run init_services.py first.")
            return
        
        # Create service associations for each stylist
        for stylist in stylists:
            for service in services:
                # Randomly allow/disallow some services
                is_allowed = random.choice([True, True, True, False])  # 75% chance
                add_service_association(stylist, service, is_allowed)
                
                # Add custom timings for allowed services
                if is_allowed:
                    custom_duration = service.duration + random.randint(-10, 10)
                    custom_duration = max(15, custom_duration)  # Minimum 15 minutes
                    add_stylist_timing(stylist, service, custom_duration)
        
        # 6. Create Appointments with Costs
        print("\n📅 Creating appointments...")
        appointment_dates = [
            date.today() - timedelta(days=7),
            date.today() - timedelta(days=5),
            date.today() - timedelta(days=3),
            date.today() - timedelta(days=1),
            date.today(),
            date.today() + timedelta(days=1),
            date.today() + timedelta(days=3),
            date.today() + timedelta(days=5)
        ]
        
        start_times = [
            time(9, 0), time(10, 30), time(12, 0), time(13, 30), 
            time(15, 0), time(16, 30)
        ]
        
        # Create appointments for each stylist
        for stylist in stylists:
            for i in range(3):  # 3 appointments per stylist
                appointment_date = random.choice(appointment_dates)
                start_time = random.choice(start_times)
                service = random.choice(services)
                customer = random.choice(customers)
                
                add_appointment(customer, stylist, service, appointment_date, start_time)
        
        # 7. Ensure billing elements exist
        print("\n💰 Checking billing elements...")
        billing_elements = BillingElement.query.all()
        if not billing_elements:
            print("⚠️ No billing elements found. Please run migrate_commission_system.py first.")
        
        # 8. Create salon settings if they don't exist
        print("\n🏪 Creating salon settings...")
        if not SalonSettings.query.first():
            default_hours = {
                'monday': {'open': '09:00', 'close': '18:00'},
                'tuesday': {'open': '09:00', 'close': '18:00'},
                'wednesday': {'open': '09:00', 'close': '18:00'},
                'thursday': {'open': '09:00', 'close': '18:00'},
                'friday': {'open': '09:00', 'close': '18:00'},
                'saturday': {'open': '09:00', 'close': '17:00'},
                'sunday': {'open': '10:00', 'close': '16:00'}
            }
            
            salon_settings = SalonSettings(
                salon_name='Salon ESE Test',
                opening_hours=default_hours,
                emergency_extension_enabled=True
            )
            db.session.add(salon_settings)
            print("✅ Added salon settings")
        
        # Commit all changes
        db.session.commit()
        
        print("\n🎉 Comprehensive test data created successfully!")
        print(f"📊 Summary:")
        print(f"   - Users: {len(stylists)} stylists, {len(customers)} customers, 1 manager")
        print(f"   - Employment details: {EmploymentDetails.query.count()}")
        print(f"   - Work patterns: {WorkPattern.query.count()}")
        print(f"   - Holiday quotas: {HolidayQuota.query.count()}")
        print(f"   - Holiday requests: {HolidayRequest.query.count()}")
        print(f"   - Service associations: {StylistServiceAssociation.query.count()}")
        print(f"   - Stylist timings: {StylistServiceTiming.query.count()}")
        print(f"   - Appointments: {Appointment.query.count()}")
        print(f"   - Appointment costs: {AppointmentCost.query.count()}")
        print(f"   - Services: {Service.query.count()}")
        
        print(f"\n🔑 Test Login Credentials:")
        print(f"   Manager: manager_1 / 12345678")
        print(f"   Stylists: stylist_1, stylist_2, stylist_3 / 12345678")
        print(f"   Customers: cust_1, cust_2, cust_3, cust_4, cust_5 / 12345678")

def main():
    create_sample_data()

if __name__ == '__main__':
    main() 