from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Role, UserProfile, SalonSettings, WorkPattern, EmploymentDetails, AppointmentCost, Appointment
from app.forms import AdminUserForm, RoleAssignmentForm, SalonSettingsForm, WorkPatternForm, EmploymentDetailsForm, AdminUserAddForm, HRDashboardFilterForm
from app.extensions import db
from app.routes.main import role_required
from app.utils import uk_now
from app.services.hr_service import HRService
import json

bp = Blueprint('admin', __name__)

@bp.route('/')
@login_required
@role_required('manager')
def dashboard():
    # Get statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    customers = User.query.join(User.roles).filter(Role.name == 'customer').count()
    stylists = User.query.join(User.roles).filter(Role.name == 'stylist').count()
    
    # Get recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         title='Admin Dashboard',
                         total_users=total_users,
                         active_users=active_users,
                         customers=customers,
                         stylists=stylists,
                         recent_users=recent_users,
                         uk_now=uk_now)

@bp.route('/hr-dashboard')
@login_required
@role_required('manager')
def hr_dashboard():
    """HR dashboard with financial tracking"""
    filter_form = HRDashboardFilterForm()
    
    # Get filter parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    stylist_id = request.args.get('stylist_id', type=int)
    employment_type = request.args.get('employment_type')
    
    # Get employment summary
    employment_summary = HRService.get_employment_summary()
    
    # Get salon profit data
    salon_profit = HRService.calculate_salon_profit(date_from, date_to)
    
    # Get stylist performance data if filtered
    stylist_performance = None
    if stylist_id:
        stylist_performance = HRService.get_stylist_performance_report(stylist_id, date_from, date_to)
    
    return render_template('admin/hr_dashboard.html',
                         title='HR Dashboard',
                         employment_summary=employment_summary,
                         salon_profit=salon_profit,
                         stylist_performance=stylist_performance,
                         filter_form=filter_form,
                         date_from=date_from,
                         date_to=date_to,
                         stylist_id=stylist_id,
                         employment_type=employment_type)

@bp.route('/hr/appointment-costs')
@login_required
@role_required('manager')
def appointment_costs():
    """View appointment cost breakdowns"""
    page = request.args.get('page', 1, type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    stylist_id = request.args.get('stylist_id', type=int)
    
    # Build query with join to appointment
    query = AppointmentCost.query.join(AppointmentCost.appointment)
    
    if date_from:
        query = query.filter(Appointment.appointment_date >= date_from)
    if date_to:
        query = query.filter(Appointment.appointment_date <= date_to)
    if stylist_id:
        query = query.filter(AppointmentCost.stylist_id == stylist_id)
    
    # Order by appointment date (most recent first)
    query = query.order_by(Appointment.appointment_date.desc())
    
    costs = query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/appointment_costs.html',
                         title='Appointment Costs',
                         costs=costs,
                         date_from=date_from,
                         date_to=date_to,
                         stylist_id=stylist_id)

@bp.route('/hr/stylist-earnings')
@login_required
@role_required('manager')
def stylist_earnings():
    """View stylist earnings reports"""
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Get all stylists
    from app.models import User, Role
    stylists = User.query.join(User.roles).filter(Role.name == 'stylist').all()
    
    # Calculate earnings for each stylist
    stylist_earnings = []
    for stylist in stylists:
        earnings = HRService.calculate_stylist_earnings(stylist.id, date_from, date_to)
        stylist_earnings.append({
            'stylist': stylist,
            'earnings': earnings
        })
    
    # Sort by total earnings (highest first)
    stylist_earnings.sort(key=lambda x: x['earnings']['total_earnings'], reverse=True)
    
    return render_template('admin/stylist_earnings.html',
                         title='Stylist Earnings',
                         stylist_earnings=stylist_earnings,
                         date_from=date_from,
                         date_to=date_to)

@bp.route('/users')
@login_required
@role_required('manager')
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', title='User Management', users=users)

@bp.route('/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserForm(obj=user)
    form.user = user
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone = form.phone.data
        user.is_active = form.is_active.data
        user.email_verified = form.email_verified.data
        
        # Handle role assignment
        new_role_name = form.roles.data
        new_role = Role.query.filter_by(name=new_role_name).first()
        
        if new_role:
            # Remove existing roles and add new one
            user.roles.clear()
            user.roles.append(new_role)
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    # Pre-populate form
    if user.roles:
        form.roles.data = user.roles[0].name
    
    return render_template('admin/edit_user.html', title='Edit User', form=form, user=user)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def add_user():
    form = AdminUserAddForm()
    
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            email_verified=True  # Admin-created users are verified
        )
        user.set_password(form.password.data)
        
        # Assign role
        role = Role.query.filter_by(name=form.role.data).first()
        if role:
            user.roles.append(role)
        
        db.session.add(user)
        db.session.commit()
        
        # Create employment details if stylist/manager/owner
        if form.role.data in ['stylist', 'manager', 'owner'] and form.employment_type.data:
            employment_details = EmploymentDetails(
                user_id=user.id,
                employment_type=form.employment_type.data
            )
            db.session.add(employment_details)
            db.session.commit()
        
        flash(f'User {user.first_name} {user.last_name} created successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/add_user.html', title='Add New User', form=form)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('owner')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the last owner
    if user.has_role('owner') and User.query.join(User.roles).filter(Role.name == 'owner').count() <= 1:
        flash('Cannot delete the last owner account.', 'error')
        return redirect(url_for('admin.users'))
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('Cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/roles', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def manage_roles():
    form = RoleAssignmentForm()
    
    if form.validate_on_submit():
        user = User.query.get(form.user_id.data)
        role = Role.query.filter_by(name=form.role_name.data).first()
        
        if user and role:
            # Remove existing roles and add new one
            user.roles.clear()
            user.roles.append(role)
            db.session.commit()
            flash(f'Role {role.name} assigned to {user.first_name} {user.last_name} successfully!', 'success')
        else:
            flash('User or role not found.', 'error')
        
        return redirect(url_for('admin.manage_roles'))
    
    # Get all roles and their user counts
    roles = Role.query.all()
    role_stats = {}
    for role in roles:
        role_stats[role.name] = User.query.join(User.roles).filter(Role.name == role.name).count()
    
    return render_template('admin/manage_roles.html', 
                         title='Role Management',
                         form=form,
                         roles=roles,
                         role_stats=role_stats)

@bp.route('/system')
@login_required
@role_required('owner')
def system_settings():
    from app.models import User, Role, UserProfile, LoginAttempt
    return render_template('admin/system_settings.html', 
                         title='System Settings',
                         User=User,
                         Role=Role,
                         UserProfile=UserProfile,
                         LoginAttempt=LoginAttempt,
                         uk_now=uk_now)

# ============================================================================
# NEW SALON MANAGEMENT ROUTES
# ============================================================================

@bp.route('/salon-settings', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def salon_settings():
    """Manage salon settings and opening hours"""
    # Get current salon settings
    salon_settings = SalonSettings.get_settings()
    
    # Create form with existing settings
    form = SalonSettingsForm(salon_settings=salon_settings)
    
    if form.validate_on_submit():
        try:
            # Update salon settings
            salon_settings.salon_name = form.salon_name.data
            salon_settings.emergency_extension_enabled = form.emergency_extension_enabled.data
            salon_settings.opening_hours = form.get_opening_hours_dict()
            
            db.session.commit()
            flash('Salon settings updated successfully!', 'success')
            return redirect(url_for('admin.salon_settings'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating salon settings: {str(e)}', 'error')
    elif form.errors:
        # If form has validation errors, show them
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    # If form has errors or is GET request, return 200 status to show form with errors
    return render_template('admin/salon_settings.html', 
                         title='Salon Settings',
                         form=form,
                         salon_settings=salon_settings)

# ============================================================================
# WORK PATTERNS AND EMPLOYMENT MANAGEMENT ROUTES
# ============================================================================

@bp.route('/work-patterns')
@login_required
@role_required('manager')
def work_patterns():
    """List all work patterns"""
    
    # Get all work patterns with user information
    patterns = db.session.query(WorkPattern, User).join(
        User, WorkPattern.user_id == User.id
    ).order_by(User.first_name, User.last_name, WorkPattern.pattern_name).all()
    
    return render_template('admin/work_patterns.html', 
                         title='Work Patterns',
                         patterns=patterns)

@bp.route('/work-patterns/new', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def new_work_pattern():
    """Create a new work pattern"""
    
    form = WorkPatternForm()
    
    if form.validate_on_submit():
        try:
            work_pattern = WorkPattern(
                user_id=form.user_id.data,
                pattern_name=form.pattern_name.data,
                work_schedule=form.get_work_schedule_dict(),
                is_active=form.is_active.data
            )
            
            db.session.add(work_pattern)
            db.session.commit()
            
            flash('Work pattern created successfully!', 'success')
            return redirect(url_for('admin.work_patterns'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating work pattern: {str(e)}', 'error')
    
    return render_template('admin/work_pattern_form.html', 
                         title='New Work Pattern',
                         form=form,
                         action='Create')

@bp.route('/work-patterns/<int:pattern_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def edit_work_pattern(pattern_id):
    """Edit an existing work pattern"""
    
    work_pattern = WorkPattern.query.get_or_404(pattern_id)
    form = WorkPatternForm(work_pattern=work_pattern)
    
    if form.validate_on_submit():
        try:
            work_pattern.user_id = form.user_id.data
            work_pattern.pattern_name = form.pattern_name.data
            work_pattern.work_schedule = form.get_work_schedule_dict()
            work_pattern.is_active = form.is_active.data
            
            db.session.commit()
            
            flash('Work pattern updated successfully!', 'success')
            return redirect(url_for('admin.work_patterns'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating work pattern: {str(e)}', 'error')
    elif form.errors:
        # If form has validation errors, show them
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return render_template('admin/work_pattern_form.html', 
                         title='Edit Work Pattern',
                         form=form,
                         work_pattern=work_pattern,
                         action='Update')

@bp.route('/work-patterns/<int:pattern_id>/delete', methods=['POST'])
@login_required
@role_required('manager')
def delete_work_pattern(pattern_id):
    """Delete a work pattern"""
    
    work_pattern = WorkPattern.query.get_or_404(pattern_id)
    
    try:
        db.session.delete(work_pattern)
        db.session.commit()
        flash('Work pattern deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting work pattern: {str(e)}', 'error')
    
    return redirect(url_for('admin.work_patterns'))

@bp.route('/employment-details')
@login_required
@role_required('manager')
def employment_details():
    """List all employment details"""
    
    # Get all employment details with user information
    details = db.session.query(EmploymentDetails, User).join(
        User, EmploymentDetails.user_id == User.id
    ).order_by(User.first_name, User.last_name).all()
    
    return render_template('admin/employment_details.html', 
                         title='Employment Details',
                         details=details)

@bp.route('/employment-details/new', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def new_employment_details():
    """Create new employment details"""
    
    form = EmploymentDetailsForm()
    
    if form.validate_on_submit():
        try:
            employment_details = EmploymentDetails(
                user_id=form.user_id.data,
                employment_type=form.employment_type.data,
                commission_percentage=float(form.commission_percentage.data) if form.commission_percentage.data else None,
                billing_method=form.billing_method.data,
                job_role=form.job_role.data,
                # HR System Integration - New Fields
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                hourly_rate=float(form.hourly_rate.data) if form.hourly_rate.data else None,
                commission_rate=float(form.commission_rate.data) if form.commission_rate.data else None,
                base_salary=float(form.base_salary.data) if form.base_salary.data else None
            )
            
            db.session.add(employment_details)
            db.session.commit()
            
            flash('Employment details created successfully!', 'success')
            return redirect(url_for('admin.employment_details'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating employment details: {str(e)}', 'error')
    
    return render_template('admin/employment_details_form.html', 
                         title='New Employment Details',
                         form=form,
                         action='Create')

@bp.route('/employment-details/<int:details_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def edit_employment_details(details_id):
    """Edit existing employment details"""
    
    employment_details = EmploymentDetails.query.get_or_404(details_id)
    form = EmploymentDetailsForm(employment_details=employment_details)
    
    if form.validate_on_submit():
        try:
            employment_details.user_id = form.user_id.data
            employment_details.employment_type = form.employment_type.data
            employment_details.commission_percentage = float(form.commission_percentage.data) if form.commission_percentage.data else None
            employment_details.billing_method = form.billing_method.data
            employment_details.job_role = form.job_role.data
            # HR System Integration - New Fields
            employment_details.start_date = form.start_date.data
            employment_details.end_date = form.end_date.data
            employment_details.hourly_rate = float(form.hourly_rate.data) if form.hourly_rate.data else None
            employment_details.commission_rate = float(form.commission_rate.data) if form.commission_rate.data else None
            employment_details.base_salary = float(form.base_salary.data) if form.base_salary.data else None
            
            db.session.commit()
            
            flash('Employment details updated successfully!', 'success')
            return redirect(url_for('admin.employment_details'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating employment details: {str(e)}', 'error')
    elif form.errors:
        # If form has validation errors, show them
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return render_template('admin/employment_details_form.html', 
                         title='Edit Employment Details',
                         form=form,
                         employment_details=employment_details,
                         action='Update')

@bp.route('/employment-details/<int:details_id>/delete', methods=['POST'])
@login_required
@role_required('manager')
def delete_employment_details(details_id):
    """Delete employment details"""
    
    employment_details = EmploymentDetails.query.get_or_404(details_id)
    
    try:
        db.session.delete(employment_details)
        db.session.commit()
        flash('Employment details deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting employment details: {str(e)}', 'error')
    
    return redirect(url_for('admin.employment_details')) 