#!/usr/bin/env python3
"""
Comprehensive test data creation with proper seniority role hierarchy:
- Owner, Manager, Senior Stylists, Stylists, Junior Stylists
- Customers with realistic names
- Employment details matching seniority levels
- Work patterns and holiday quotas
- Service associations and timings
- Sample appointments with cost calculations
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
    """Add a user with specified roles"""
    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"User {username} already exists")
        return existing
    
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
        email_verified=True
    )
    user.set_password(password)
    
    for role in roles:
        user.roles.append(role)
    
    db.session.add(user)
    db.session.flush()
    print(f"✅ Created user: {first_name} {last_name} ({username}) - {[r.name for r in roles]}")
    return user

def add_employment_details(user, employment_type, commission_rate=None, hourly_rate=None, base_salary=None, job_role=None):
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
        billing_method='salon_bills',
        job_role=job_role,
        start_date=date.today() - timedelta(days=random.randint(30, 365))
    )
    db.session.add(employment)
    print(f"💼 Added employment for {user.username}: {employment_type} - {job_role}")
    return employment

def add_work_pattern(user, pattern_type='full_time'):
    """Add work pattern for a user"""
    existing = WorkPattern.query.filter_by(user_id=user.id).first()
    if existing:
        print(f"Work pattern already exists for {user.username}")
        return existing
    
    if pattern_type == 'full_time':
        work_schedule = {
            'monday': {'working': True, 'start': '09:00', 'end': '17:00'},
            'tuesday': {'working': True, 'start': '09:00', 'end': '17:00'},
            'wednesday': {'working': True, 'start': '09:00', 'end': '17:00'},
            'thursday': {'working': True, 'start': '09:00', 'end': '17:00'},
            'friday': {'working': True, 'start': '09:00', 'end': '17:00'},
            'saturday': {'working': True, 'start': '09:00', 'end': '16:00'},
            'sunday': {'working': False, 'start': None, 'end': None}
        }
    elif pattern_type == 'part_time':
        work_schedule = {
            'monday': {'working': True, 'start': '10:00', 'end': '16:00'},
            'tuesday': {'working': True, 'start': '10:00', 'end': '16:00'},
            'wednesday': {'working': True, 'start': '10:00', 'end': '16:00'},
            'thursday': {'working': True, 'start': '10:00', 'end': '16:00'},
            'friday': {'working': True, 'start': '10:00', 'end': '16:00'},
            'saturday': {'working': True, 'start': '09:00', 'end': '15:00'},
            'sunday': {'working': False, 'start': None, 'end': None}
        }
    else:  # weekend_specialist
        work_schedule = {
            'monday': {'working': True, 'start': '10:00', 'end': '16:00'},
            'tuesday': {'working': True, 'start': '10:00', 'end': '16:00'},
            'wednesday': {'working': True, 'start': '10:00', 'end': '16:00'},
            'thursday': {'working': True, 'start': '10:00', 'end': '16:00'},
            'friday': {'working': True, 'start': '10:00', 'end': '16:00'},
            'saturday': {'working': True, 'start': '08:00', 'end': '18:00'},
            'sunday': {'working': True, 'start': '09:00', 'end': '17:00'}
        }
    
    work_pattern = WorkPattern(
        user_id=user.id,
        pattern_name=f"{pattern_type.title()} Pattern",
        work_schedule=work_schedule,
        is_active=True
    )
    db.session.add(work_pattern)
    print(f"📅 Added {pattern_type} work pattern for {user.username}")
    return work_pattern

def add_holiday_quota(user, days=25):
    """Add holiday quota for a user"""
    existing = HolidayQuota.query.filter_by(user_id=user.id).first()
    if existing:
        print(f"Holiday quota already exists for {user.username}")
        return existing
    
    # Calculate weekly hours (assuming full-time for simplicity)
    weekly_hours = 40 if days >= 25 else 20
    
    quota = HolidayQuota(
        user_id=user.id,
        year=date.today().year,
        total_hours_per_week=weekly_hours,
        holiday_days_entitled=days,
        holiday_days_taken=random.randint(0, days // 2),
        holiday_days_remaining=days - random.randint(0, days // 2)
    )
    db.session.add(quota)
    print(f"🏖️ Added holiday quota for {user.username}: {days} days")
    return quota

def add_service_associations(stylist, services, timing_multiplier=1.0):
    """Add service associations for a stylist"""
    for service in services:
        existing = StylistServiceAssociation.query.filter_by(
            stylist_id=stylist.id, service_id=service.id
        ).first()
        if existing:
            continue
        
        association = StylistServiceAssociation(
            stylist_id=stylist.id,
            service_id=service.id,
            is_allowed=True
        )
        db.session.add(association)
        
        # Add timing
        timing = StylistServiceTiming(
            stylist_id=stylist.id,
            service_id=service.id,
            custom_duration=int(service.duration * timing_multiplier),
            custom_waiting_time=int(service.waiting_time * timing_multiplier) if service.waiting_time else None
        )
        db.session.add(timing)
    
    print(f"🔗 Added service associations for {stylist.username}")

def add_appointment(customer, stylist, service, appointment_date, start_time, status='confirmed'):
    """Add appointment with cost calculation"""
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
    db.session.flush()
    
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
            # Handle both dictionary and object return types
            if isinstance(cost_data, dict):
                appointment_cost = AppointmentCost(
                    appointment_id=appointment.id,
                    stylist_id=stylist.id,
                    service_revenue=service.price,
                    stylist_cost=cost_data.get('stylist_cost', 0),
                    salon_profit=cost_data.get('salon_profit', 0),
                    calculation_method=cost_data.get('calculation_method', 'commission'),
                    hours_worked=cost_data.get('hours_worked'),
                    commission_amount=cost_data.get('commission_amount'),
                    commission_breakdown=cost_data.get('commission_breakdown')
                )
                db.session.add(appointment_cost)
            else:
                # cost_data is already an AppointmentCost object
                cost_data.appointment_id = appointment.id
                cost_data.stylist_id = stylist.id
                cost_data.service_revenue = service.price
    
    print(f"📅 Added {status} appointment: {customer.first_name} with {stylist.first_name} - {service.name}")
    return appointment

def create_ranked_test_data():
    """Create comprehensive test data with proper seniority hierarchy"""
    app = create_app()
    
    with app.app_context():
        print("🎯 Creating comprehensive test data with seniority hierarchy...")
        
        # Get all roles
        owner_role = get_role('owner')
        manager_role = get_role('manager')
        senior_stylist_role = get_role('senior_stylist')
        stylist_role = get_role('stylist')
        junior_stylist_role = get_role('junior_stylist')
        customer_role = get_role('customer')
        
        if not all([owner_role, manager_role, senior_stylist_role, stylist_role, junior_stylist_role, customer_role]):
            print("❌ Required roles do not exist. Please run add_seniority_roles.py first.")
            return
        
        # 1. Create Management Team
        print("\n👑 Creating management team...")
        manager = add_user(
            username='salon_manager',
            email='manager@salon-ese.com',
            first_name='Sarah',
            last_name='Mitchell',
            password='12345678',
            roles=[manager_role]
        )
        
        # 2. Create Stylists with Seniority Hierarchy
        print("\n👥 Creating stylists with seniority hierarchy...")
        
        # Senior Stylists (experienced, high commission)
        senior_stylists = []
        senior_names = [
            ('Emma', 'Wilson', 'emma_wilson'),
            ('James', 'Brown', 'james_brown'),
            ('Sophie', 'Davis', 'sophie_davis')
        ]
        
        for first_name, last_name, username in senior_names:
            stylist = add_user(
                username=username,
                email=f'{username}@salon-ese.com',
                first_name=first_name,
                last_name=last_name,
                password='12345678',
                roles=[senior_stylist_role]
            )
            senior_stylists.append(stylist)
        
        # Regular Stylists (mid-level)
        stylists = []
        stylist_names = [
            ('Michael', 'Taylor', 'michael_taylor'),
            ('Olivia', 'Anderson', 'olivia_anderson'),
            ('David', 'Martinez', 'david_martinez'),
            ('Lisa', 'Thompson', 'lisa_thompson')
        ]
        
        for first_name, last_name, username in stylist_names:
            stylist = add_user(
                username=username,
                email=f'{username}@salon-ese.com',
                first_name=first_name,
                last_name=last_name,
                password='12345678',
                roles=[stylist_role]
            )
            stylists.append(stylist)
        
        # Junior Stylists (new/training)
        junior_stylists = []
        junior_names = [
            ('Alex', 'Johnson', 'alex_johnson'),
            ('Maya', 'Garcia', 'maya_garcia'),
            ('Ryan', 'Lee', 'ryan_lee')
        ]
        
        for first_name, last_name, username in junior_names:
            stylist = add_user(
                username=username,
                email=f'{username}@salon-ese.com',
                first_name=first_name,
                last_name=last_name,
                password='12345678',
                roles=[junior_stylist_role]
            )
            junior_stylists.append(stylist)
        
        # 3. Create Customers
        print("\n👥 Creating customers...")
        customers = []
        customer_names = [
            ('Alice', 'Johnson', 'alice_j'),
            ('Bob', 'Smith', 'bob_smith'),
            ('Carol', 'Williams', 'carol_w'),
            ('Dan', 'Jones', 'dan_jones'),
            ('Eve', 'Garcia', 'eve_garcia'),
            ('Frank', 'Miller', 'frank_m'),
            ('Grace', 'Davis', 'grace_d'),
            ('Henry', 'Rodriguez', 'henry_r'),
            ('Ivy', 'Martinez', 'ivy_m'),
            ('Jack', 'Hernandez', 'jack_h'),
            ('Kate', 'Lopez', 'kate_lopez'),
            ('Leo', 'Gonzalez', 'leo_g'),
            ('Maya', 'Perez', 'maya_p'),
            ('Nick', 'Turner', 'nick_t'),
            ('Opal', 'Phillips', 'opal_p')
        ]
        
        for first_name, last_name, username in customer_names:
            customer = add_user(
                username=username,
                email=f'{username}@example.com',
                first_name=first_name,
                last_name=last_name,
                password='12345678',
                roles=[customer_role]
            )
            customers.append(customer)
        
        # 4. Create Employment Details with Seniority-Based Compensation
        print("\n💼 Creating employment details...")
        
        # Manager - Good salary
        add_employment_details(manager, 'employed', base_salary=Decimal('45000.00'), job_role='Salon Manager')
        
        # Senior Stylists - High commission rates
        for stylist in senior_stylists:
            add_employment_details(stylist, 'self_employed', commission_rate=Decimal('75.00'), job_role='Senior Stylist')
        
        # Regular Stylists - Medium commission rates
        for stylist in stylists:
            add_employment_details(stylist, 'self_employed', commission_rate=Decimal('65.00'), job_role='Stylist')
        
        # Junior Stylists - Lower commission rates or hourly
        for i, stylist in enumerate(junior_stylists):
            if i % 2 == 0:
                add_employment_details(stylist, 'employed', hourly_rate=Decimal('12.00'), base_salary=Decimal('18000.00'), job_role='Junior Stylist')
            else:
                add_employment_details(stylist, 'self_employed', commission_rate=Decimal('50.00'), job_role='Junior Stylist')
        
        # 5. Create Work Patterns
        print("\n📅 Creating work patterns...")
        
        # Senior stylists - full time
        for stylist in senior_stylists:
            add_work_pattern(stylist, 'full_time')
        
        # Regular stylists - mix of patterns
        for i, stylist in enumerate(stylists):
            pattern = 'full_time' if i < 2 else 'part_time'
            add_work_pattern(stylist, pattern)
        
        # Junior stylists - part time or weekend specialist
        for i, stylist in enumerate(junior_stylists):
            pattern = 'part_time' if i < 2 else 'weekend_specialist'
            add_work_pattern(stylist, pattern)
        
        # 6. Create Holiday Quotas
        print("\n🏖️ Creating holiday quotas...")
        
        # Senior stylists - more holiday days
        for stylist in senior_stylists:
            add_holiday_quota(stylist, 30)
        
        # Regular stylists - standard holiday days
        for stylist in stylists:
            add_holiday_quota(stylist, 25)
        
        # Junior stylists - fewer holiday days
        for stylist in junior_stylists:
            add_holiday_quota(stylist, 20)
        
        # 7. Create Services
        print("\n💇 Creating services...")
        services = []
        
        service_data = [
            ('Haircut', 45, 15, Decimal('35.00')),
            ('Haircut & Style', 60, 20, Decimal('45.00')),
            ('Haircut & Blow Dry', 75, 25, Decimal('55.00')),
            ('Full Haircut & Style', 90, 30, Decimal('65.00')),
            ('Hair Color', 120, 30, Decimal('85.00')),
            ('Highlights', 150, 45, Decimal('95.00')),
            ('Balayage', 180, 60, Decimal('120.00')),
            ('Hair Extensions', 240, 60, Decimal('200.00')),
            ('Keratin Treatment', 180, 45, Decimal('150.00')),
            ('Hair Treatment', 60, 20, Decimal('40.00'))
        ]
        
        for name, duration, waiting_time, price in service_data:
            service = Service(
                name=name,
                description=f"Professional {name.lower()} service",
                duration=duration,
                waiting_time=waiting_time,
                price=price,
                is_active=True
            )
            db.session.add(service)
            services.append(service)
        
        db.session.flush()
        
        # 8. Create Service Associations with Seniority-Based Access
        print("\n🔗 Creating service associations...")
        
        # Senior stylists - all services, faster timing
        for stylist in senior_stylists:
            add_service_associations(stylist, services, 0.8)  # 20% faster
        
        # Regular stylists - most services, standard timing
        for stylist in stylists:
            add_service_associations(stylist, services[:-2], 1.0)  # Exclude most complex services
        
        # Junior stylists - basic services, slower timing
        basic_services = services[:5]  # Only basic services
        for stylist in junior_stylists:
            add_service_associations(stylist, basic_services, 1.2)  # 20% slower
        
        # 9. Create Sample Appointments
        print("\n📅 Creating sample appointments...")
        
        all_stylists = senior_stylists + stylists + junior_stylists
        statuses = ['confirmed', 'completed', 'cancelled', 'no-show']
        
        # Create appointments for the next 2 weeks
        for i in range(14):
            appointment_date = date.today() + timedelta(days=i)
            
            # Create 3-8 appointments per day
            num_appointments = random.randint(3, 8)
            for _ in range(num_appointments):
                customer = random.choice(customers)
                stylist = random.choice(all_stylists)
                
                # Get stylist's services
                stylist_services = Service.query.join(StylistServiceAssociation).filter(
                    StylistServiceAssociation.stylist_id == stylist.id
                ).all()
                
                if stylist_services:
                    service = random.choice(stylist_services)
                    start_hour = random.randint(9, 16)
                    start_minute = random.choice([0, 15, 30, 45])
                    start_time = time(start_hour, start_minute)
                    status = random.choice(statuses)
                    
                    add_appointment(customer, stylist, service, appointment_date, start_time, status)
        
        # 10. Create Salon Settings
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
                salon_name='Salon ESE - Premium Hair Services',
                opening_hours=default_hours,
                emergency_extension_enabled=True
            )
            db.session.add(salon_settings)
        
        # Commit all changes
        db.session.commit()
        
        print("\n🎉 Comprehensive test data created successfully!")
        print(f"\n📊 Summary:")
        print(f"   - Management: 1 Manager (Owner account to be created separately)")
        print(f"   - Senior Stylists: {len(senior_stylists)} (High commission, all services)")
        print(f"   - Regular Stylists: {len(stylists)} (Medium commission, most services)")
        print(f"   - Junior Stylists: {len(junior_stylists)} (Lower commission, basic services)")
        print(f"   - Customers: {len(customers)}")
        print(f"   - Services: {len(services)}")
        print(f"   - Appointments: {Appointment.query.count()}")
        
        print(f"\n🔑 Test Login Credentials:")
        print(f"   Manager: salon_manager / 12345678")
        print(f"   Senior Stylists: emma_wilson, james_brown, sophie_davis / 12345678")
        print(f"   Regular Stylists: michael_taylor, olivia_anderson, david_martinez, lisa_thompson / 12345678")
        print(f"   Junior Stylists: alex_johnson, maya_garcia, ryan_lee / 12345678")
        print(f"   Customers: alice_j, bob_smith, carol_w, dan_jones, eve_garcia / 12345678")
        print(f"\n📝 Note: Owner account should be created separately via registration")

if __name__ == '__main__':
    create_ranked_test_data() 