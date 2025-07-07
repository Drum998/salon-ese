from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models import User, UserProfile
from app.forms import ProfileForm, StylistProfileForm, CustomerProfileForm, ChangePasswordForm
from app.extensions import db
import os
from werkzeug.utils import secure_filename
import json

bp = Blueprint('profile', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/profile')
@login_required
def view_profile():
    return render_template('profile/view_profile.html', title='My Profile')

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Get or create user profile
    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    # Choose appropriate form based on user's primary role
    if current_user.has_role('stylist'):
        form = StylistProfileForm(obj=profile)
        form.user_id = current_user.id
    elif current_user.has_role('customer'):
        form = CustomerProfileForm(obj=profile)
        form.user_id = current_user.id
    else:
        form = ProfileForm(obj=profile)
        form.user_id = current_user.id
    
    if form.validate_on_submit():
        # Update user basic info
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        
        # Update profile info
        profile.bio = form.bio.data
        profile.date_of_birth = form.date_of_birth.data
        profile.address = form.address.data
        profile.emergency_contact = form.emergency_contact.data
        profile.emergency_phone = form.emergency_phone.data
        
        # Handle profile image upload
        if form.profile_image.data:
            file = form.profile_image.data
            if file and allowed_file(file.filename):
                filename = secure_filename(f"profile_{current_user.id}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                
                # Ensure upload directory exists
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                file.save(filepath)
                profile.profile_image = filename
        
        # Handle role-specific fields
        if current_user.has_role('stylist'):
            if form.specialties.data:
                profile.specialties = json.dumps([s.strip() for s in form.specialties.data.split(',')])
            if form.experience_years.data:
                profile.experience_years = int(form.experience_years.data)
            if form.certifications.data:
                profile.certifications = json.dumps([c.strip() for c in form.certifications.data.split(',')])
        
        elif current_user.has_role('customer'):
            profile.hair_type = form.hair_type.data
            if form.allergies.data:
                profile.allergies = json.dumps([a.strip() for a in form.allergies.data.split(',')])
            profile.notes = form.notes.data
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.view_profile'))
    
    # Pre-populate form with existing data
    if profile.specialties:
        try:
            specialties = json.loads(profile.specialties)
            form.specialties.data = ', '.join(specialties)
        except:
            form.specialties.data = profile.specialties
    
    if profile.certifications:
        try:
            certifications = json.loads(profile.certifications)
            form.certifications.data = ', '.join(certifications)
        except:
            form.certifications.data = profile.certifications
    
    if profile.allergies:
        try:
            allergies = json.loads(profile.allergies)
            form.allergies.data = ', '.join(allergies)
        except:
            form.allergies.data = profile.allergies
    
    return render_template('profile/edit_profile.html', title='Edit Profile', form=form)

@bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('profile.view_profile'))
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('profile/change_password.html', title='Change Password', form=form) 