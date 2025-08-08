from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user, login_required
from app.models import User, Role, Service, Appointment, AppointmentStatus, AppointmentService, StylistServiceAssociation
from app.forms import AppointmentBookingForm, AppointmentManagementForm, AppointmentFilterForm, ServiceForm, StylistServiceTimingForm
from app.extensions import db
from app.services.hr_service import HRService
from app.services.salon_hours_service import SalonHoursService
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
    
    # Handle pre-filled parameters from click-to-book
    if request.method == 'GET':
        # Pre-fill date if provided
        if request.args.get('date'):
            try:
                pre_filled_date = datetime.strptime(request.args.get('date'), '%Y-%m-%d').date()
                form.appointment_date.data = pre_filled_date
            except ValueError:
                pass
        
        # Pre-fill time if provided
        if request.args.get('time'):
            pre_filled_time = request.args.get('time')
            if pre_filled_time in [choice[0] for choice in form.start_time.choices]:
                form.start_time.data = pre_filled_time
        
        # Pre-fill stylist if provided
        if request.args.get('stylist_id'):
            try:
                pre_filled_stylist_id = int(request.args.get('stylist_id'))
                if pre_filled_stylist_id in [choice[0] for choice in form.stylist_id.choices]:
                    form.stylist_id.data = pre_filled_stylist_id
            except ValueError:
                pass
    
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
        
        # Validate appointment time against salon hours
        validation = SalonHoursService.validate_appointment_time(
            form.appointment_date.data,
            start_time,
            end_time,
            form.stylist_id.data,
            allow_emergency=form.emergency_extension.data
        )
        
        if not validation['valid']:
            flash(validation['reason'], 'error')
            return redirect(url_for('appointments.book_appointment'))
        
        # Show warning for emergency extensions
        if validation.get('emergency_extension'):
            flash(validation['warning'], 'warning')
        
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
        
        # Create the appointment
        appointment = Appointment(
            customer_id=form.customer_id.data,
            stylist_id=form.stylist_id.data,
            booked_by_id=current_user.id,
            appointment_date=form.appointment_date.data,
            start_time=start_time,
            end_time=end_time,
            customer_phone=form.customer_phone.data,
            customer_email=form.customer_email.data,
            notes=form.notes.data,
            status='confirmed'
        )
        
        # Add appointment to database and get ID
        db.session.add(appointment)
        db.session.flush()  # Get the ID without committing
        
        # Add services to the appointment
        for i, service_form in enumerate(form.services.entries):
            if service_form.service_id.data:
                appointment_service = AppointmentService(
                    appointment_id=appointment.id,
                    service_id=service_form.service_id.data,
                    duration=service_form.duration.data,
                    waiting_time=service_form.waiting_time.data,
                    order=i
                )
                db.session.add(appointment_service)
        
        # Create status history entry
        status_entry = AppointmentStatus(
            appointment_id=appointment.id,
            status='confirmed',
            changed_by_id=current_user.id,
            notes='Appointment booked'
        )
        db.session.add(status_entry)
        
        # Calculate appointment costs using HR service
        try:
            HRService.calculate_appointment_cost(appointment.id)
        except Exception as e:
            logging.error(f"Error calculating appointment cost: {e}")
        
        db.session.commit()
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointments.view_appointment', appointment_id=appointment.id))
    
    # Get salon settings for display
    salon_settings = SalonHoursService.get_salon_settings()
    
    return render_template('appointments/book.html', 
                         title='Book Appointment',
                         form=form,
                         salon_settings=salon_settings)

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
    
    # Populate form with current filter values to maintain state
    form.view_type.data = view_type
    
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
    role_filter = request.args.get('role_filter', '')
    selected_date = request.args.get('date', date.today().isoformat())
    
    # Populate form with current filter values to maintain state
    form.view_type.data = view_type
    form.stylist_id.data = stylist_id
    form.status.data = status_filter
    
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
    
    # Get all stylists for the calendar columns with role filtering and seniority ordering
    stylist_query = User.query.join(User.roles).filter(
        Role.name.in_(['stylist', 'manager', 'owner', 'senior_stylist', 'junior_stylist'])
    )
    
    # Apply role filter if specified
    if role_filter:
        stylist_query = stylist_query.filter(Role.name == role_filter)
    
    # Order by seniority: owner, manager, senior_stylist, stylist, junior_stylist
    from sqlalchemy import case
    seniority_order = case(
        (Role.name == 'owner', 1),
        (Role.name == 'manager', 2),
        (Role.name == 'senior_stylist', 3),
        (Role.name == 'stylist', 4),
        (Role.name == 'junior_stylist', 5),
        else_=6
    )
    
    stylists = stylist_query.order_by(seniority_order, User.first_name, User.last_name).all()
    
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
                         stylists=stylists,
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
        
        # HR System Integration - Recalculate cost if status changed to completed
        if old_status != form.status.data and form.status.data == 'completed':
            try:
                cost_record = HRService.calculate_appointment_cost(appointment.id)
                if cost_record:
                    current_app.logger.info(f"Cost recalculated for completed appointment {appointment.id}: "
                                           f"Revenue £{cost_record.service_revenue}, "
                                           f"Stylist Cost £{cost_record.stylist_cost}, "
                                           f"Profit £{cost_record.salon_profit}")
            except Exception as e:
                current_app.logger.error(f"Failed to recalculate cost for appointment {appointment.id}: {str(e)}")
        
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
    """Enhanced services management with stylist-service matrix"""
    services = Service.query.order_by(Service.name).all()
    stylists = User.query.join(User.roles).filter(
        Role.name.in_(['stylist', 'manager', 'owner'])
    ).order_by(User.first_name, User.last_name).all()
    
    # Get existing associations for the matrix
    associations = StylistServiceAssociation.query.all()
    stylist_service_associations = {}
    
    for association in associations:
        stylist_service_associations[(association.stylist_id, association.service_id)] = association
    
    return render_template('appointments/services.html',
                         services=services,
                         stylists=stylists,
                         stylist_service_associations=stylist_service_associations,
                         title='Manage Services')


@bp.route('/services/bulk-update-associations', methods=['POST'])
@login_required
@roles_required('manager', 'owner')
def bulk_update_associations():
    """Bulk update stylist-service associations from matrix"""
    try:
        data = request.get_json()
        associations_data = data.get('associations', [])
        
        if not associations_data:
            return jsonify({'success': False, 'error': 'No associations data provided'})
        
        # Process each association
        for assoc_data in associations_data:
            stylist_id = assoc_data.get('stylist_id')
            service_id = assoc_data.get('service_id')
            is_allowed = assoc_data.get('is_allowed', False)
            
            if not stylist_id or not service_id:
                continue
            
            # Check if association exists
            existing_association = StylistServiceAssociation.query.filter_by(
                stylist_id=stylist_id,
                service_id=service_id
            ).first()
            
            if existing_association:
                # Update existing association
                existing_association.is_allowed = is_allowed
            else:
                # Create new association only if it's allowed (to avoid unnecessary restrictions)
                if is_allowed:
                    new_association = StylistServiceAssociation(
                        stylist_id=stylist_id,
                        service_id=service_id,
                        is_allowed=True
                    )
                    db.session.add(new_association)
        
        db.session.commit()
        
        # Log the bulk update
        current_app.logger.info(f"Bulk stylist-service associations updated by user {current_user.id} ({current_user.username})")
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in bulk_update_associations: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

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

@bp.route('/api/available-slots')
@login_required
def api_available_slots():
    """API endpoint to get available time slots for a date and stylist"""
    date_str = request.args.get('date')
    stylist_id = request.args.get('stylist_id', type=int)
    
    if not date_str:
        return jsonify({'error': 'Date parameter is required'}), 400
    
    try:
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Get available slots
    available_slots = SalonHoursService.generate_available_time_slots(
        appointment_date, 
        stylist_id
    )
    
    # Get salon hours for this date
    hours = SalonHoursService.get_opening_hours_for_date(appointment_date)
    salon_hours = None
    if hours:
        salon_hours = {
            'open': hours['open'].strftime('%H:%M'),
            'close': hours['close'].strftime('%H:%M'),
            'closed': hours['closed']
        }
    
    return jsonify({
        'slots': available_slots,
        'salon_hours': salon_hours,
        'date': date_str
    }) 