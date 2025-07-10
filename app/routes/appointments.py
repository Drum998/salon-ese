from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user, login_required
from app.models import User, Role, Service, Appointment, AppointmentStatus
from app.forms import AppointmentBookingForm, AppointmentManagementForm, AppointmentFilterForm, ServiceForm
from app.extensions import db
from datetime import datetime, date, timedelta
from functools import wraps
import calendar
import logging

bp = Blueprint('appointments', __name__)

def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if not current_user.can_access(role_name):
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@bp.route('/book', methods=['GET', 'POST'])
@login_required
@role_required('customer')
def book_appointment():
    form = AppointmentBookingForm()
    
    if form.validate_on_submit():
        # Get the selected service to calculate end time
        service = Service.query.get(form.service_id.data)
        if not service:
            flash('Selected service not found.', 'error')
            return redirect(url_for('appointments.book_appointment'))
        
        # Parse start time and calculate end time
        start_time = datetime.strptime(form.start_time.data, '%H:%M').time()
        start_datetime = datetime.combine(form.appointment_date.data, start_time)
        end_datetime = start_datetime + timedelta(minutes=service.duration)
        end_time = end_datetime.time()
        
        # Check for conflicts
        conflicts = Appointment.query.filter(
            Appointment.stylist_id == form.stylist_id.data,
            Appointment.appointment_date == form.appointment_date.data,
            Appointment.status.in_(['confirmed', 'completed']),
            db.or_(
                db.and_(
                    Appointment.start_time <= start_time,
                    Appointment.end_time > start_time
                ),
                db.and_(
                    Appointment.start_time < end_time,
                    Appointment.end_time >= end_time
                ),
                db.and_(
                    Appointment.start_time >= start_time,
                    Appointment.end_time <= end_time
                )
            )
        ).first()
        
        if conflicts:
            flash('This time slot conflicts with an existing appointment. Please choose a different time.', 'error')
            return redirect(url_for('appointments.book_appointment'))
        
        # Create the appointment
        appointment = Appointment(
            customer_id=current_user.id,
            stylist_id=form.stylist_id.data,
            service_id=form.service_id.data,
            appointment_date=form.appointment_date.data,
            start_time=start_time,
            end_time=end_time,
            customer_phone=form.customer_phone.data or current_user.phone,
            customer_email=form.customer_email.data or current_user.email,
            notes=form.notes.data
        )
        
        db.session.add(appointment)
        db.session.flush()  # This gets the ID without committing
        
        # Create initial status record
        status_record = AppointmentStatus(
            appointment_id=appointment.id,
            status='confirmed',
            changed_by_id=current_user.id
        )
        db.session.add(status_record)
        
        db.session.commit()
        
        # Log the booking
        current_app.logger.info(f"Appointment booked: ID {appointment.id}, Customer {appointment.customer.first_name} {appointment.customer.last_name}, "
                               f"Stylist {appointment.stylist.first_name} {appointment.stylist.last_name}, "
                               f"Service {appointment.service.name}, Date {appointment.appointment_date}, Time {appointment.start_time}")
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointments.my_appointments'))
    
    return render_template('appointments/book.html', form=form, title='Book Appointment')

@bp.route('/my-appointments')
@login_required
@role_required('customer')
def my_appointments():
    appointments = Appointment.query.filter_by(customer_id=current_user.id)\
        .order_by(Appointment.appointment_date, Appointment.start_time).all()
    
    return render_template('appointments/my_appointments.html', 
                         appointments=appointments, title='My Appointments')

@bp.route('/stylist-appointments')
@login_required
@role_required('stylist')
def stylist_appointments():
    form = AppointmentFilterForm()
    
    # Get filter parameters
    view_type = request.args.get('view_type', 'week')
    selected_date = request.args.get('date', date.today().isoformat())
    
    try:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        selected_date = date.today()
    
    # Calculate date range based on view type
    if view_type == 'week':
        start_date = selected_date - timedelta(days=selected_date.weekday())
        end_date = start_date + timedelta(days=6)
    else:  # month view
        start_date = selected_date.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Get appointments for the stylist in the date range
    appointments = Appointment.query.filter(
        Appointment.stylist_id == current_user.id,
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    ).order_by(Appointment.appointment_date, Appointment.start_time).all()
    
    # Log debug information
    current_app.logger.info(f"Stylist {current_user.id} ({current_user.first_name} {current_user.last_name}) calendar view:")
    current_app.logger.info(f"  Date range: {start_date} to {end_date}")
    current_app.logger.info(f"  View type: {view_type}")
    current_app.logger.info(f"  Total appointments found: {len(appointments)}")
    for apt in appointments:
        current_app.logger.info(f"    - {apt.appointment_date} at {apt.start_time}: {apt.customer.first_name} {apt.customer.last_name} ({apt.service.name})")
    
    # Create a helper function to get appointments for a specific time slot
    def get_appointments_for_slot(appointments, target_date, target_hour, target_minute):
        return [apt for apt in appointments 
                if apt.appointment_date == target_date 
                and apt.start_time.hour == target_hour 
                and apt.start_time.minute == target_minute]
    
    return render_template('appointments/stylist_calendar.html',
                         appointments=appointments,
                         start_date=start_date,
                         end_date=end_date,
                         view_type=view_type,
                         selected_date=selected_date,
                         form=form,
                         title='My Appointments',
                         timedelta=timedelta,
                         calendar=calendar,
                         date=date,
                         get_appointments_for_slot=get_appointments_for_slot)

@bp.route('/admin-appointments')
@login_required
@role_required('manager')
def admin_appointments():
    form = AppointmentFilterForm()
    
    # Get filter parameters
    view_type = request.args.get('view_type', 'week')
    stylist_id = request.args.get('stylist_id', '')
    status_filter = request.args.get('status', '')
    selected_date = request.args.get('date', date.today().isoformat())
    
    try:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        selected_date = date.today()
    
    # Calculate date range based on view type
    if view_type == 'week':
        start_date = selected_date - timedelta(days=selected_date.weekday())
        end_date = start_date + timedelta(days=6)
    else:  # month view
        start_date = selected_date.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Build query
    query = Appointment.query.filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    )
    
    if stylist_id:
        query = query.filter(Appointment.stylist_id == stylist_id)
    
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    appointments = query.order_by(Appointment.appointment_date, Appointment.start_time).all()
    
    # Create a helper function to get appointments for a specific time slot
    def get_appointments_for_slot(appointments, target_date, target_hour, target_minute):
        return [apt for apt in appointments 
                if apt.appointment_date == target_date 
                and apt.start_time.hour == target_hour 
                and apt.start_time.minute == target_minute]
    
    return render_template('appointments/admin_calendar.html',
                         appointments=appointments,
                         start_date=start_date,
                         end_date=end_date,
                         view_type=view_type,
                         selected_date=selected_date,
                         form=form,
                         title='All Appointments',
                         timedelta=timedelta,
                         calendar=calendar,
                         date=date,
                         get_appointments_for_slot=get_appointments_for_slot)

@bp.route('/appointment/<int:appointment_id>')
@login_required
def view_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check permissions
    if not (current_user.has_role('manager') or 
            current_user.has_role('owner') or 
            appointment.customer_id == current_user.id or 
            appointment.stylist_id == current_user.id):
        flash('You do not have permission to view this appointment.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('appointments/view_appointment.html',
                         appointment=appointment,
                         title='Appointment Details')

@bp.route('/appointment/<int:appointment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check permissions
    if not (current_user.has_role('manager') or 
            current_user.has_role('owner') or 
            appointment.stylist_id == current_user.id):
        flash('You do not have permission to edit this appointment.', 'error')
        return redirect(url_for('main.index'))
    
    form = AppointmentManagementForm(obj=appointment)
    
    if form.validate_on_submit():
        old_status = appointment.status
        appointment.status = form.status.data
        appointment.notes = form.notes.data
        
        # Create status history record if status changed
        if old_status != form.status.data:
            status_record = AppointmentStatus(
                appointment_id=appointment.id,
                status=form.status.data,
                notes=form.notes.data,
                changed_by_id=current_user.id
            )
            db.session.add(status_record)
        
        db.session.commit()
        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('appointments.view_appointment', appointment_id=appointment.id))
    
    return render_template('appointments/edit_appointment.html',
                         form=form,
                         appointment=appointment,
                         title='Edit Appointment')

@bp.route('/appointment/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check permissions - customers can cancel their own appointments, stylists/managers can cancel any
    if not (current_user.has_role('manager') or 
            current_user.has_role('owner') or 
            appointment.stylist_id == current_user.id or 
            appointment.customer_id == current_user.id):
        flash('You do not have permission to cancel this appointment.', 'error')
        return redirect(url_for('main.index'))
    
    # Check if appointment can be cancelled (not in the past and not already cancelled)
    if appointment.is_past:
        flash('Cannot cancel appointments in the past.', 'error')
        return redirect(url_for('appointments.view_appointment', appointment_id=appointment.id))
    
    if appointment.status == 'cancelled':
        flash('Appointment is already cancelled.', 'error')
        return redirect(url_for('appointments.view_appointment', appointment_id=appointment.id))
    
    # Cancel the appointment
    old_status = appointment.status
    appointment.status = 'cancelled'
    
    # Create status history record
    status_record = AppointmentStatus(
        appointment_id=appointment.id,
        status='cancelled',
        notes=f'Cancelled by {current_user.first_name} {current_user.last_name}',
        changed_by_id=current_user.id
    )
    db.session.add(status_record)
    db.session.commit()
    
    flash('Appointment cancelled successfully!', 'success')
    return redirect(url_for('appointments.view_appointment', appointment_id=appointment.id))

@bp.route('/services')
@login_required
@role_required('manager')
def manage_services():
    services = Service.query.order_by(Service.name).all()
    return render_template('appointments/services.html',
                         services=services,
                         title='Manage Services')

@bp.route('/services/new', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def new_service():
    form = ServiceForm()
    
    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            description=form.description.data,
            duration=int(form.duration.data),
            price=float(form.price.data),
            is_active=form.is_active.data
        )
        db.session.add(service)
        db.session.commit()
        flash('Service created successfully!', 'success')
        return redirect(url_for('appointments.manage_services'))
    
    return render_template('appointments/service_form.html',
                         form=form,
                         title='New Service')

@bp.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceForm(obj=service)
    
    if form.validate_on_submit():
        service.name = form.name.data
        service.description = form.description.data
        service.duration = int(form.duration.data)
        service.price = float(form.price.data)
        service.is_active = form.is_active.data
        
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('appointments.manage_services'))
    
    return render_template('appointments/service_form.html',
                         form=form,
                         service=service,
                         title='Edit Service')

# API endpoints for calendar data
@bp.route('/api/appointments')
@login_required
def api_appointments():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    stylist_id = request.args.get('stylist_id')
    
    if not start_date or not end_date:
        return jsonify([])
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify([])
    
    query = Appointment.query.filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    )
    
    # Filter by stylist if specified
    if stylist_id and current_user.has_role('manager'):
        query = query.filter(Appointment.stylist_id == stylist_id)
    elif current_user.has_role('stylist'):
        query = query.filter(Appointment.stylist_id == current_user.id)
    elif current_user.has_role('customer'):
        query = query.filter(Appointment.customer_id == current_user.id)
    
    appointments = query.all()
    
    events = []
    for appointment in appointments:
        events.append({
            'id': appointment.id,
            'title': f"{appointment.customer.first_name} {appointment.customer.last_name} - {appointment.service.name}",
            'start': f"{appointment.appointment_date.isoformat()}T{appointment.start_time.isoformat()}",
            'end': f"{appointment.appointment_date.isoformat()}T{appointment.end_time.isoformat()}",
            'status': appointment.status,
            'url': url_for('appointments.view_appointment', appointment_id=appointment.id)
        })
    
    return jsonify(events) 