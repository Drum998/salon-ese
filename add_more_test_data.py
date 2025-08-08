#!/usr/bin/env python3
"""
Enhanced script to add additional test data:
- 6 new stylists with employment details, work patterns, and holiday quotas
- 20 new customers
- Sample appointments using existing services and new users
- Service associations and timings for new stylists

This extends the existing test data from add_test_users.py
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
        manager = User.query.filter_by(username='manager_1').first()
        if manager:
            request.approved_by_id = manager.id
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
                    commission_breakdown=cost_data.get('commission_breakdown'),
                    billing_method=cost_data.get('billing_method'),
                    billing_elements_applied=cost_data.get('billing_elements_applied')
                )
            else:
                # cost_data is already an AppointmentCost object
                appointment_cost = cost_data
                appointment_cost.appointment_id = appointment.id
                appointment_cost.stylist_id = stylist.id
                appointment_cost.service_revenue = service.price
            
            db.session.add(appointment_cost)
    
    print(f"Added appointment: {customer.username} with {stylist.username} - {service.name} on {appointment_date}")
    return appointment

def create_additional_data():
    """Create additional test data with 6 new stylists and 20 new customers"""
    app = create_app()
    
    with app.app_context():
        print("🎯 Creating additional test data...")
        
        # Get roles
        stylist_role = get_role('stylist')
        customer_role = get_role('customer')
        
        if not (stylist_role and customer_role):
            print("❌ Required roles do not exist. Please ensure roles are seeded.")
            return
        
        # 1. Create 6 New Stylists
        print("\n👥 Creating 6 new stylists...")
        new_stylists = []
        stylist_names = [
            ('Emma', 'Wilson', 'emma_wilson'),
            ('James', 'Brown', 'james_brown'),
            ('Sophie', 'Davis', 'sophie_davis'),
            ('Michael', 'Taylor', 'michael_taylor'),
            ('Olivia', 'Anderson', 'olivia_anderson'),
            ('David', 'Martinez', 'david_martinez')
        ]
        
        for i, (first_name, last_name, username) in enumerate(stylist_names):
            stylist = add_user(
                username=username,
                email=f'{username}@example.com',
                first_name=first_name,
                last_name=last_name,
                password='12345678',
                roles=[stylist_role]
            )
            new_stylists.append(stylist)
        
        # 2. Create 20 New Customers
        print("\n👥 Creating 20 new customers...")
        new_customers = []
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
            ('Opal', 'Phillips', 'opal_p'),
            ('Paul', 'Campbell', 'paul_c'),
            ('Quinn', 'Parker', 'quinn_p'),
            ('Rose', 'Evans', 'rose_e'),
            ('Sam', 'Edwards', 'sam_e'),
            ('Tina', 'Collins', 'tina_c')
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
            new_customers.append(customer)
        
        # 3. Create Employment Details for New Stylists
        print("\n💼 Creating employment details for new stylists...")
        # Mix of employment types
        employment_configs = [
            ('self_employed', Decimal('80.00'), None, None),  # High commission
            ('self_employed', Decimal('70.00'), None, None),  # Medium commission
            ('employed', None, Decimal('15.00'), Decimal('25000.00')),  # Hourly + salary
            ('self_employed', Decimal('75.00'), None, None),  # High commission
            ('employed', None, Decimal('13.50'), Decimal('22000.00')),  # Hourly + salary
            ('self_employed', Decimal('65.00'), None, None),  # Medium commission
        ]
        
        for i, stylist in enumerate(new_stylists):
            emp_type, commission, hourly, salary = employment_configs[i]
            add_employment_details(stylist, emp_type, commission, hourly, salary)
        
        # 4. Create Work Patterns for New Stylists
        print("\n📅 Creating work patterns for new stylists...")
        # Different work patterns
        full_time_schedule = {
            'monday': {'start': '09:00', 'end': '18:00', 'working': True},
            'tuesday': {'start': '09:00', 'end': '18:00', 'working': True},
            'wednesday': {'start': '09:00', 'end': '18:00', 'working': True},
            'thursday': {'start': '09:00', 'end': '18:00', 'working': True},
            'friday': {'start': '09:00', 'end': '18:00', 'working': True},
            'saturday': {'start': '09:00', 'end': '17:00', 'working': True},
            'sunday': {'start': '09:00', 'end': '17:00', 'working': False}
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
        
        weekend_schedule = {
            'monday': {'start': '09:00', 'end': '18:00', 'working': False},
            'tuesday': {'start': '09:00', 'end': '18:00', 'working': False},
            'wednesday': {'start': '09:00', 'end': '18:00', 'working': False},
            'thursday': {'start': '09:00', 'end': '18:00', 'working': False},
            'friday': {'start': '09:00', 'end': '18:00', 'working': False},
            'saturday': {'start': '09:00', 'end': '18:00', 'working': True},
            'sunday': {'start': '09:00', 'end': '18:00', 'working': True}
        }
        
        work_patterns = [
            ('Full Time', full_time_schedule),
            ('Part Time', part_time_schedule),
            ('Full Time', full_time_schedule),
            ('Weekend Specialist', weekend_schedule),
            ('Part Time', part_time_schedule),
            ('Full Time', full_time_schedule)
        ]
        
        for i, stylist in enumerate(new_stylists):
            pattern_name, schedule = work_patterns[i]
            add_work_pattern(stylist, pattern_name, schedule)
        
        # 5. Create Holiday Quotas and Requests for New Stylists
        print("\n🏖️ Creating holiday data for new stylists...")
        current_year = date.today().year
        
        for stylist in new_stylists:
            hours_per_week = random.choice([32, 37, 40, 25, 30, 35])
            add_holiday_quota(stylist, current_year, hours_per_week)
        
        # Add some holiday requests for new stylists
        add_holiday_request(
            new_stylists[0], 
            date.today() + timedelta(days=45), 
            date.today() + timedelta(days=49), 
            'approved'
        )
        add_holiday_request(
            new_stylists[2], 
            date.today() + timedelta(days=75), 
            date.today() + timedelta(days=77), 
            'pending'
        )
        add_holiday_request(
            new_stylists[4], 
            date.today() + timedelta(days=120), 
            date.today() + timedelta(days=125), 
            'approved'
        )
        
        # 6. Get services and create associations for new stylists
        print("\n🔗 Creating service associations for new stylists...")
        services = Service.query.all()
        if not services:
            print("⚠️ No services found. Please run init_services.py first.")
            return
        
        # Create service associations for each new stylist
        for stylist in new_stylists:
            for service in services:
                # Randomly allow/disallow some services (80% chance of allowing)
                is_allowed = random.choice([True, True, True, True, False])
                add_service_association(stylist, service, is_allowed)
                
                # Add custom timings for allowed services
                if is_allowed:
                    custom_duration = service.duration + random.randint(-15, 15)
                    custom_duration = max(15, custom_duration)  # Minimum 15 minutes
                    add_stylist_timing(stylist, service, custom_duration)
        
        # 7. Create Appointments with New Users
        print("\n📅 Creating appointments with new users...")
        
        # Get all stylists (existing + new)
        all_stylists = User.query.filter(User.roles.any(name='stylist')).all()
        all_customers = User.query.filter(User.roles.any(name='customer')).all()
        
        # Create more diverse appointment dates
        appointment_dates = [
            date.today() - timedelta(days=14),
            date.today() - timedelta(days=12),
            date.today() - timedelta(days=10),
            date.today() - timedelta(days=8),
            date.today() - timedelta(days=6),
            date.today() - timedelta(days=4),
            date.today() - timedelta(days=2),
            date.today() - timedelta(days=1),
            date.today(),
            date.today() + timedelta(days=1),
            date.today() + timedelta(days=2),
            date.today() + timedelta(days=4),
            date.today() + timedelta(days=6),
            date.today() + timedelta(days=8),
            date.today() + timedelta(days=10),
            date.today() + timedelta(days=12),
            date.today() + timedelta(days=14)
        ]
        
        start_times = [
            time(9, 0), time(9, 30), time(10, 0), time(10, 30), time(11, 0), time(11, 30),
            time(12, 0), time(12, 30), time(13, 0), time(13, 30), time(14, 0), time(14, 30),
            time(15, 0), time(15, 30), time(16, 0), time(16, 30), time(17, 0)
        ]
        
        # Create appointments for each stylist (mix of existing and new)
        for stylist in all_stylists:
            # Create 4-6 appointments per stylist
            num_appointments = random.randint(4, 6)
            for i in range(num_appointments):
                appointment_date = random.choice(appointment_dates)
                start_time = random.choice(start_times)
                service = random.choice(services)
                customer = random.choice(all_customers)
                
                # Random status (mostly confirmed, some completed, few cancelled)
                status = random.choices(
                    ['confirmed', 'completed', 'cancelled', 'no_show'],
                    weights=[70, 20, 8, 2]
                )[0]
                
                add_appointment(customer, stylist, service, appointment_date, start_time, status)
        
        # 8. Create some multi-service appointments
        print("\n🔄 Creating multi-service appointments...")
        for i in range(10):  # Create 10 multi-service appointments
            stylist = random.choice(all_stylists)
            customer = random.choice(all_customers)
            appointment_date = random.choice(appointment_dates)
            start_time = random.choice(start_times)
            
            # Select 2-3 services for multi-service appointment
            selected_services = random.sample(services, min(3, len(services)))
            
            # Create the main appointment
            main_service = selected_services[0]
            appointment = Appointment(
                customer_id=customer.id,
                stylist_id=stylist.id,
                booked_by_id=customer.id,
                appointment_date=appointment_date,
                start_time=start_time,
                end_time=datetime.combine(appointment_date, start_time) + timedelta(minutes=sum(s.duration for s in selected_services)),
                status='confirmed',
                notes=f"Multi-service appointment for {customer.username} with {stylist.username}"
            )
            db.session.add(appointment)
            db.session.flush()
            
            # Add all services to the appointment
            current_time = start_time
            for order, service in enumerate(selected_services, 1):
                appointment_service = AppointmentService(
                    appointment_id=appointment.id,
                    service_id=service.id,
                    duration=service.duration,
                    waiting_time=service.waiting_time,
                    order=order
                )
                db.session.add(appointment_service)
                current_time = (datetime.combine(date.today(), current_time) + timedelta(minutes=service.duration)).time()
            
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
                            service_revenue=sum(s.price for s in selected_services),
                            stylist_cost=cost_data.get('stylist_cost', 0),
                            salon_profit=cost_data.get('salon_profit', 0),
                            calculation_method=cost_data.get('calculation_method', 'commission'),
                            hours_worked=cost_data.get('hours_worked'),
                            commission_amount=cost_data.get('commission_amount'),
                            commission_breakdown=cost_data.get('commission_breakdown'),
                            billing_method=cost_data.get('billing_method'),
                            billing_elements_applied=cost_data.get('billing_elements_applied')
                        )
                    else:
                        # cost_data is already an AppointmentCost object
                        appointment_cost = cost_data
                        appointment_cost.appointment_id = appointment.id
                        appointment_cost.stylist_id = stylist.id
                        appointment_cost.service_revenue = sum(s.price for s in selected_services)
                    
                    db.session.add(appointment_cost)
            
            print(f"Added multi-service appointment: {customer.username} with {stylist.username} - {len(selected_services)} services on {appointment_date}")
        
        # Commit all changes
        db.session.commit()
        
        print("\n🎉 Additional test data created successfully!")
        print(f"📊 Summary:")
        print(f"   - New Stylists: {len(new_stylists)}")
        print(f"   - New Customers: {len(new_customers)}")
        print(f"   - Total Users: {User.query.count()}")
        print(f"   - Total Stylists: {User.query.filter(User.roles.any(name='stylist')).count()}")
        print(f"   - Total Customers: {User.query.filter(User.roles.any(name='customer')).count()}")
        print(f"   - Total Appointments: {Appointment.query.count()}")
        print(f"   - Total Employment Details: {EmploymentDetails.query.count()}")
        print(f"   - Total Work Patterns: {WorkPattern.query.count()}")
        print(f"   - Total Holiday Quotas: {HolidayQuota.query.count()}")
        print(f"   - Total Holiday Requests: {HolidayRequest.query.count()}")
        print(f"   - Total Service Associations: {StylistServiceAssociation.query.count()}")
        print(f"   - Total Stylist Timings: {StylistServiceTiming.query.count()}")
        print(f"   - Total Appointment Costs: {AppointmentCost.query.count()}")
        
        print(f"\n🔑 New Test Login Credentials:")
        print(f"   New Stylists: emma_wilson, james_brown, sophie_davis, michael_taylor, olivia_anderson, david_martinez / 12345678")
        print(f"   New Customers: alice_j, bob_smith, carol_w, dan_jones, eve_garcia, frank_m, grace_d, henry_r, ivy_m, jack_h, kate_lopez, leo_g, maya_p, nick_t, opal_p, paul_c, quinn_p, rose_e, sam_e, tina_c / 12345678")

def main():
    create_additional_data()

if __name__ == '__main__':
    main() 