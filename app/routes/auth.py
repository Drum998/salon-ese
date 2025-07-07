from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Role, LoginAttempt
from app.forms import LoginForm, RegistrationForm
from app.extensions import db
from datetime import datetime
import json

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # Log login attempt
        login_attempt = LoginAttempt(
            user_id=user.id if user else None,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            success=False
        )
        
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            login_attempt.success = True
            db.session.add(login_attempt)
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
            db.session.add(login_attempt)
            db.session.commit()
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        
        # Check if this is the first user (make them owner)
        if User.query.count() == 0:
            owner_role = Role.query.filter_by(name='owner').first()
            if owner_role:
                user.roles.append(owner_role)
            user.email_verified = True  # First user is automatically verified
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/profile')
@login_required
def profile():
    return redirect(url_for('profile.view_profile')) 