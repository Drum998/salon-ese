from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Role, UserProfile
from app.forms import AdminUserForm, RoleAssignmentForm
from app.extensions import db
from app.routes.main import role_required
from app.utils import uk_now
import json

bp = Blueprint('admin', __name__)

@bp.route('/admin')
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

@bp.route('/admin/users')
@login_required
@role_required('manager')
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', title='User Management', users=users)

@bp.route('/admin/users/<int:user_id>', methods=['GET', 'POST'])
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

@bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
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

@bp.route('/admin/roles', methods=['GET', 'POST'])
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

@bp.route('/admin/system')
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