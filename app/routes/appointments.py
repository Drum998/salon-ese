from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user, login_required
from app.models import User, Role, Service, Appointment, AppointmentStatus, AppointmentService, StylistServiceAssociation
from app.forms import AppointmentBookingForm, AppointmentManagementForm, AppointmentFilterForm, ServiceForm, StylistServiceTimingForm, StylistServiceAssociationForm
from app.extensions import db
from datetime import datetime, date, timedelta
from functools import wraps
import calendar
import logging

bp = Blueprint('appointments', __name__)

def roles_required(*role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if not any(current_user.has_role(role) for role in role_names):
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@bp.route('/book', methods=['GET', 'POST'])
@login_required
@roles_required('customer', 'stylist', 'manager', 'owner')
def book_appointment():
    form = AppointmentBookingForm()
    
    # Populate service choices for each subform
    services = Service.query.filter_by(is_active=True).all()
    service_choices = [(s.id, f"{s.name} (£{s.price}) - {s.duration}min") for s in services]
    for subform in form.services:
        subform.service_id.choices = service_choices
    
    if form.validate_on_submit():
        # Parse start time
        start_time = datetime.strptime(form.start_time.data, '%H:%M').time()
        start_datetime = datetime.combine(form.appointment_date.data, start_time)
        
        # Calculate total duration (sum of all services)
        total_duration = 0
        for service_form in form.services.entries:
            total_duration += (service_form.duration.data or 0)
            if service_form.waiting_time.data:
                total_duration += service_form.waiting_time.data
        end_datetime = start_datetime + timedelta(minutes=total_duration)
        end_time = end_datetime.time()
        
        # Check for conflicts (same as before, but for total duration)
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
        
        # Create the appointment (service_id is deprecated, set to first service for legacy compatibility)
        first_service_id = form.services.entries[0].service_id.data if form.services.entries else None
        appointment = Appointment(
            customer_id=form.customer_id.data,
            stylist_id=form.stylist_id.data,
            service_id=first_service_id,
            appointment_date=form.appointment_date.data,
            start_time=start_time,
            end_time=end_time,
            customer_phone=form.customer_phone.data or current_user.phone,
            customer_email=form.customer_email.data or current_user.email,
            notes=form.notes.data,
            booked_by_id=current_user.id
        )
        db.session.add(appointment)
        db.session.flush()  # Get appointment.id
        
        # Create AppointmentService entries
        for idx, service_form in enumerate(form.services.entries):
            # Check if stylist timing should be used
            duration_to_use = service_form.duration.data
            if service_form.use_stylist_timing.data:
                from app.models import StylistServiceTiming
                stylist_timing = StylistServiceTiming.get_stylist_duration(
                    form.stylist_id.data, 
                    service_form.service_id.data
                )
                if stylist_timing:
                    duration_to_use = stylist_timing
            
            appt_service = AppointmentService(
                appointment_id=appointment.id,
                service_id=service_form.service_id.data,
                duration=duration_to_use,
                waiting_time=service_form.waiting_time.data or 0,
                order=idx
            )
            db.session.add(appt_service)
        
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
                               f"Services {[s.service_id.data for s in form.services.entries]}, Date {appointment.appointment_date}, Time {appointment.start_time}")
        
        flash('Appointment booked successfully!', 'success')
        # Redirect based on role
        if current_user.has_role('customer'):
            return redirect(url_for('appointments.my_appointments'))
        elif current_user.has_role('stylist'):
            return redirect(url_for('appointments.stylist_appointments'))
        elif current_user.has_role('manager') or current_user.has_role('owner'):
            return redirect(url_for('appointments.admin_appointments'))
        else:
            return redirect(url_for('main.index'))
    else:
        # Debug: Show validation errors
        if form.errors:
            current_app.logger.error(f"Form validation errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error in {field}: {error}', 'error')
    
    return render_template('appointments/book.html', form=form, title='Book Appointment')

@bp.route('/my-appointments')
@login_required
@roles_required('customer', 'stylist', 'manager', 'owner')
def my_appointments():
    appointments = Appointment.query.filter_by(customer_id=current_user.id)\
        .order_by(Appointment.appointment_date, Appointment.start_time).all()
    
    return render_template('appointments/my_appointments.html', 
                         appointments=appointments, title='My Appointments')

@bp.route('/stylist-appointments')
@login_required
@roles_required('stylist', 'manager', 'owner')
def stylist_appointments():
    form = AppointmentFilterForm()
    
    # Get filter parameters
    view_type = request.args.get('view_type', 'week')
    calendar_view = request.args.get('calendar_view', 'personal')  # personal or global
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
    
    # Get appointments based on calendar view
    if calendar_view == 'global':
        # Show all appointments in the salon for the date range
        appointments = Appointment.query.filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).order_by(Appointment.appointment_date, Appointment.start_time).all()
    else:
        # Show only the current stylist's appointments
        appointments = Appointment.query.filter(
            Appointment.stylist_id == current_user.id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).order_by(Appointment.appointment_date, Appointment.start_time).all()
    
    # Log debug information
    current_app.logger.info(f"Stylist {current_user.id} ({current_user.first_name} {current_user.last_name}) calendar view:")
    current_app.logger.info(f"  Date range: {start_date} to {end_date}")
    current_app.logger.info(f"  View type: {view_type}")
    current_app.logger.info(f"  Calendar view: {calendar_view}")
    current_app.logger.info(f"  Total appointments found: {len(appointments)}")
    for apt in appointments:
        current_app.logger.info(f"    - {apt.appointment_date} at {apt.start_time}: {apt.customer.first_name} {apt.customer.last_name} ({apt.service.name}) - Stylist: {apt.stylist.first_name} {apt.stylist.last_name}")
    
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
                         calendar_view=calendar_view,
                         selected_date=selected_date,
                         form=form,
                         title='My Appointments' if calendar_view == 'personal' else 'Salon Schedule',
                         timedelta=timedelta,
                         calendar=calendar,
                         date=date,
                         get_appointments_for_slot=get_appointments_for_slot)

@bp.route('/admin-appointments')
@login_required
@roles_required('manager', 'owner')
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
    
    # Handle stylist_id filter with proper type conversion
    if stylist_id and stylist_id.strip():
        try:
            stylist_id_int = int(stylist_id)
            query = query.filter(Appointment.stylist_id == stylist_id_int)
        except ValueError:
            # If stylist_id is not a valid integer, ignore the filter
            pass
    
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
@roles_required('manager', 'owner')
def manage_services():
    services = Service.query.order_by(Service.name).all()
    return render_template('appointments/services.html',
                         services=services,
                         title='Manage Services')

@bp.route('/services/new', methods=['GET', 'POST'])
@login_required
@roles_required('manager', 'owner')
def new_service():
    form = ServiceForm()
    
    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            description=form.description.data,
            duration=int(form.duration.data),
            waiting_time=int(form.waiting_time.data) if form.waiting_time.data else None,
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
@roles_required('manager', 'owner')
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceForm(obj=service)
    
    if form.validate_on_submit():
        service.name = form.name.data
        service.description = form.description.data
        service.duration = int(form.duration.data)
        service.waiting_time = int(form.waiting_time.data) if form.waiting_time.data else None
        service.price = float(form.price.data)
        service.is_active = form.is_active.data
        
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('appointments.manage_services'))
    
    return render_template('appointments/service_form.html',
                         form=form,
                         service=service,
                         title='Edit Service')

@bp.route('/stylist-timings')
@login_required
@roles_required('manager', 'owner')
def manage_stylist_timings():
    from app.models import StylistServiceTiming
    timings = StylistServiceTiming.query.join(StylistServiceTiming.stylist).join(StylistServiceTiming.service).order_by(
        StylistServiceTiming.stylist_id, StylistServiceTiming.service_id
    ).all()
    return render_template('appointments/stylist_timings.html',
                         timings=timings,
                         title='Manage Stylist Timings')

@bp.route('/stylist-timings/new', methods=['GET', 'POST'])
@login_required
@roles_required('manager', 'owner')
def new_stylist_timing():
    from app.models import StylistServiceTiming
    form = StylistServiceTimingForm()
    
    if form.validate_on_submit():
        # Check if timing already exists for this stylist-service combination
        existing_timing = StylistServiceTiming.query.filter_by(
            stylist_id=form.stylist_id.data,
            service_id=form.service_id.data
        ).first()
        
        if existing_timing:
            # Update existing timing
            existing_timing.custom_duration = int(form.custom_duration.data)
            existing_timing.custom_waiting_time = int(form.custom_waiting_time.data) if form.custom_waiting_time.data else None
            existing_timing.notes = form.notes.data
            existing_timing.is_active = form.is_active.data
            flash('Stylist timing updated successfully!', 'success')
        else:
            # Create new timing
            timing = StylistServiceTiming(
                stylist_id=form.stylist_id.data,
                service_id=form.service_id.data,
                custom_duration=int(form.custom_duration.data),
                custom_waiting_time=int(form.custom_waiting_time.data) if form.custom_waiting_time.data else None,
                notes=form.notes.data,
                is_active=form.is_active.data
            )
            db.session.add(timing)
            flash('Stylist timing created successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('appointments.manage_stylist_timings'))
    
    return render_template('appointments/stylist_timing_form.html',
                         form=form,
                         title='New Stylist Timing')

@bp.route('/stylist-timings/<int:timing_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('manager', 'owner')
def edit_stylist_timing(timing_id):
    from app.models import StylistServiceTiming
    timing = StylistServiceTiming.query.get_or_404(timing_id)
    form = StylistServiceTimingForm(obj=timing)
    
    if form.validate_on_submit():
        timing.custom_duration = int(form.custom_duration.data)
        timing.custom_waiting_time = int(form.custom_waiting_time.data) if form.custom_waiting_time.data else None
        timing.notes = form.notes.data
        timing.is_active = form.is_active.data
        
        db.session.commit()
        flash('Stylist timing updated successfully!', 'success')
        return redirect(url_for('appointments.manage_stylist_timings'))
    
    return render_template('appointments/stylist_timing_form.html',
                         form=form,
                         timing=timing,
                         title='Edit Stylist Timing')

@bp.route('/stylist-timings/<int:timing_id>/delete', methods=['POST'])
@login_required
@roles_required('manager', 'owner')
def delete_stylist_timing(timing_id):
    from app.models import StylistServiceTiming
    timing = StylistServiceTiming.query.get_or_404(timing_id)
    db.session.delete(timing)
    db.session.commit()
    flash('Stylist timing deleted successfully!', 'success')
    return redirect(url_for('appointments.manage_stylist_timings'))

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
        try:
            stylist_id_int = int(stylist_id)
            query = query.filter(Appointment.stylist_id == stylist_id_int)
        except ValueError:
            # If stylist_id is not a valid integer, ignore the filter
            pass
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


# Stylist-Service Association Management Routes
@bp.route('/stylist-associations')
@login_required
@roles_required('manager', 'owner')
def manage_stylist_associations():
    """Manage which stylists can perform which services"""
    associations = StylistServiceAssociation.query.join(
        StylistServiceAssociation.stylist
    ).join(
        StylistServiceAssociation.service
    ).order_by(
        StylistServiceAssociation.stylist_id, 
        StylistServiceAssociation.service_id
    ).all()
    
    return render_template('appointments/stylist_associations.html',
                         associations=associations,
                         title='Manage Stylist-Service Associations')


@bp.route('/stylist-associations/new', methods=['GET', 'POST'])
@login_required
@roles_required('manager', 'owner')
def new_stylist_association():
    """Create a new stylist-service association"""
    form = StylistServiceAssociationForm()
    
    if form.validate_on_submit():
        # Convert string values to integers
        stylist_id = int(form.stylist_id.data)
        service_id = int(form.service_id.data)
        
        # Check if association already exists for this stylist-service combination
        existing_association = StylistServiceAssociation.query.filter_by(
            stylist_id=stylist_id,
            service_id=service_id
        ).first()
        
        if existing_association:
            # Update existing association
            existing_association.is_allowed = form.is_allowed.data
            existing_association.notes = form.notes.data
            flash('Stylist association updated successfully!', 'success')
        else:
            # Create new association
            association = StylistServiceAssociation(
                stylist_id=stylist_id,
                service_id=service_id,
                is_allowed=form.is_allowed.data,
                notes=form.notes.data
            )
            db.session.add(association)
            flash('Stylist association created successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('appointments.manage_stylist_associations'))
    
    return render_template('appointments/stylist_association_form.html',
                         form=form,
                         title='New Stylist-Service Association')


@bp.route('/stylist-associations/<int:association_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('manager', 'owner')
def edit_stylist_association(association_id):
    """Edit an existing stylist-service association"""
    association = StylistServiceAssociation.query.get_or_404(association_id)
    form = StylistServiceAssociationForm(obj=association)
    
    if form.validate_on_submit():
        # Convert string values to integers
        stylist_id = int(form.stylist_id.data)
        service_id = int(form.service_id.data)
        
        # Update the association
        association.stylist_id = stylist_id
        association.service_id = service_id
        association.is_allowed = form.is_allowed.data
        association.notes = form.notes.data
        
        db.session.commit()
        flash('Stylist association updated successfully!', 'success')
        return redirect(url_for('appointments.manage_stylist_associations'))
    
    return render_template('appointments/stylist_association_form.html',
                         form=form,
                         association=association,
                         title='Edit Stylist-Service Association')


@bp.route('/stylist-associations/<int:association_id>/delete', methods=['POST'])
@login_required
@roles_required('manager', 'owner')
def delete_stylist_association(association_id):
    """Delete a stylist-service association"""
    association = StylistServiceAssociation.query.get_or_404(association_id)
    db.session.delete(association)
    db.session.commit()
    flash('Stylist association deleted successfully!', 'success')
    return redirect(url_for('appointments.manage_stylist_associations'))


@bp.route('/api/stylist-services/<int:stylist_id>')
@login_required
def api_stylist_services(stylist_id):
    """API endpoint to get services a stylist can perform"""
    if not current_user.has_role('manager') and not current_user.has_role('owner'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    stylist = User.query.get_or_404(stylist_id)
    if not stylist.has_role('stylist'):
        return jsonify({'error': 'User is not a stylist'}), 400
    
    # Get services the stylist is allowed to perform
    allowed_services = StylistServiceAssociation.get_stylist_services(stylist_id)
    
    services_data = []
    for service in allowed_services:
        services_data.append({
            'id': service.id,
            'name': service.name,
            'duration': service.duration,
            'price': float(service.price),
            'waiting_time': service.waiting_time
        })
    
    return jsonify(services_data)


@bp.route('/api/service/<int:service_id>')
@login_required
def api_service_details(service_id):
    """API endpoint to get service details"""
    if not current_user.has_role('manager') and not current_user.has_role('owner'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    service = Service.query.get_or_404(service_id)
    
    service_data = {
        'id': service.id,
        'name': service.name,
        'duration': service.duration,
        'waiting_time': service.waiting_time,
        'price': float(service.price)
    }
    
    return jsonify(service_data) 