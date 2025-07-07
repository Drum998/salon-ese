from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models import User, Role
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
        return render_template('main/stylist_dashboard.html', title='Stylist Dashboard')
    elif current_user.has_role('customer'):
        return render_template('main/customer_dashboard.html', title='Customer Dashboard')
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