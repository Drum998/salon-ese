from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask_login import current_user, login_required
from app.models import User, Role
from app.forms import HolidayRequestForm
from app.services.holiday_service import HolidayService
from functools import wraps

bp = Blueprint('main', __name__)

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

@bp.route('/')
def index():
    return render_template('main/index.html', title='Salon ESE - Welcome')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.has_role('owner'):
        return redirect(url_for('admin.dashboard'))
    elif current_user.has_role('manager'):
        return redirect(url_for('admin.dashboard'))
    elif current_user.has_role('stylist'):
        # Get stylist's upcoming appointments
        from app.models import Appointment
        from datetime import date, timedelta
        
        today = date.today()
        upcoming_appointments = Appointment.query.filter(
            Appointment.stylist_id == current_user.id,
            Appointment.appointment_date >= today,
            Appointment.status.in_(['confirmed', 'completed'])
        ).order_by(Appointment.appointment_date, Appointment.start_time).limit(5).all()
        
        today_appointments = Appointment.query.filter(
            Appointment.stylist_id == current_user.id,
            Appointment.appointment_date == today,
            Appointment.status == 'confirmed'
        ).order_by(Appointment.start_time).all()
        
        return render_template('main/stylist_dashboard.html', 
                             title='Stylist Dashboard',
                             upcoming_appointments=upcoming_appointments,
                             today_appointments=today_appointments)
    elif current_user.has_role('customer'):
        # Get customer's appointments
        from app.models import Appointment
        from datetime import date
        
        today = date.today()
        upcoming_appointments = Appointment.query.filter(
            Appointment.customer_id == current_user.id,
            Appointment.appointment_date >= today,
            Appointment.status.in_(['confirmed', 'completed'])
        ).order_by(Appointment.appointment_date, Appointment.start_time).limit(5).all()
        
        past_appointments = Appointment.query.filter(
            Appointment.customer_id == current_user.id,
            Appointment.appointment_date < today
        ).order_by(Appointment.appointment_date.desc(), Appointment.start_time.desc()).limit(3).all()
        
        # Log debug information
        current_app.logger.info(f"Customer {current_user.id} ({current_user.first_name} {current_user.last_name}) dashboard:")
        current_app.logger.info(f"  Today: {today}")
        current_app.logger.info(f"  Upcoming appointments: {len(upcoming_appointments)}")
        current_app.logger.info(f"  Past appointments: {len(past_appointments)}")
        for apt in upcoming_appointments:
            current_app.logger.info(f"    - Upcoming: {apt.appointment_date} at {apt.start_time}: {apt.service.name} with {apt.stylist.first_name} {apt.stylist.last_name}")
        
        return render_template('main/customer_dashboard.html', 
                             title='Customer Dashboard',
                             upcoming_appointments=upcoming_appointments,
                             past_appointments=past_appointments,
                             date=date)
    else:
        return render_template('main/guest_dashboard.html', title='Guest Dashboard')

@bp.route('/about')
def about():
    return render_template('main/about.html', title='About Salon ESE')

@bp.route('/contact')
def contact():
    return render_template('main/contact.html', title='Contact Us')

@bp.route('/services')
def services():
    return render_template('main/services.html', title='Our Services')

@bp.route('/holiday-request', methods=['GET', 'POST'])
@login_required
@role_required('stylist')
def holiday_request():
    """Submit a holiday request"""
    form = HolidayRequestForm()
    
    # Get user's holiday quota
    quota = HolidayService.get_or_create_holiday_quota(current_user.id)
    
    # Get recent requests
    recent_requests = HolidayService.get_user_holiday_requests(current_user.id)[:5]
    
    if form.validate_on_submit():
        # Create the holiday request
        request_obj, errors = HolidayService.create_holiday_request(
            current_user.id,
            form.start_date.data,
            form.end_date.data,
            form.notes.data
        )
        
        if request_obj:
            flash('Holiday request submitted successfully! It will be reviewed by management.', 'success')
            return redirect(url_for('main.holiday_request'))
        else:
            for error in errors:
                flash(error, 'error')
    
    return render_template('main/holiday_request.html',
                         title='Holiday Request',
                         form=form,
                         quota=quota,
                         recent_requests=recent_requests) 