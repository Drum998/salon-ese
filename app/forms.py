from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from app.models import User, Role
import json

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email address.')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional(), Length(max=200)])
    emergency_contact = StringField('Emergency Contact', validators=[Optional(), Length(max=100)])
    emergency_phone = StringField('Emergency Phone', validators=[Optional(), Length(max=20)])
    profile_image = FileField('Profile Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Update Profile')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user.id != self.user_id:
            raise ValidationError('Email already registered. Please use a different email address.')

class StylistProfileForm(ProfileForm):
    specialties = StringField('Specialties (comma-separated)', validators=[Optional()])
    experience_years = StringField('Years of Experience', validators=[Optional()])
    certifications = StringField('Certifications (comma-separated)', validators=[Optional()])
    
    def validate_experience_years(self, experience_years):
        if experience_years.data:
            try:
                years = int(experience_years.data)
                if years < 0 or years > 50:
                    raise ValueError
            except ValueError:
                raise ValidationError('Please enter a valid number of years (0-50).')

class CustomerProfileForm(ProfileForm):
    hair_type = SelectField('Hair Type', choices=[
        ('', 'Select hair type'),
        ('straight', 'Straight'),
        ('wavy', 'Wavy'),
        ('curly', 'Curly'),
        ('coily', 'Coily'),
        ('fine', 'Fine'),
        ('thick', 'Thick'),
        ('dry', 'Dry'),
        ('oily', 'Oily')
    ], validators=[Optional()])
    allergies = StringField('Allergies (comma-separated)', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class AdminUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    is_active = BooleanField('Active')
    email_verified = BooleanField('Email Verified')
    roles = SelectField('Primary Role', choices=[
        ('guest', 'Guest'),
        ('customer', 'Customer'),
        ('stylist', 'Stylist'),
        ('manager', 'Manager'),
        ('owner', 'Owner')
    ], validators=[DataRequired()])
    submit = SubmitField('Update User')
    
    def __init__(self, user=None, *args, **kwargs):
        super(AdminUserForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def validate_username(self, username):
        if self.user and username.data == self.user.username:
            return
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')
    
    def validate_email(self, email):
        if self.user and email.data == self.user.email:
            return
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class RoleAssignmentForm(FlaskForm):
    user_id = SelectField('User', coerce=int, validators=[DataRequired()])
    role_name = SelectField('Role', choices=[
        ('guest', 'Guest'),
        ('customer', 'Customer'),
        ('stylist', 'Stylist'),
        ('manager', 'Manager'),
        ('owner', 'Owner')
    ], validators=[DataRequired()])
    submit = SubmitField('Assign Role')
    
    def __init__(self, *args, **kwargs):
        super(RoleAssignmentForm, self).__init__(*args, **kwargs)
        # Populate user choices
        users = User.query.filter_by(is_active=True).all()
        self.user_id.choices = [(user.id, f"{user.first_name} {user.last_name} ({user.username})") for user in users]

class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    duration = StringField('Duration (minutes)', validators=[DataRequired()])
    price = StringField('Price (£)', validators=[DataRequired()])
    is_active = BooleanField('Active Service', default=True)
    submit = SubmitField('Save Service')
    
    def validate_duration(self, duration):
        try:
            mins = int(duration.data)
            if mins <= 0 or mins > 480:  # Max 8 hours
                raise ValueError
        except ValueError:
            raise ValidationError('Please enter a valid duration in minutes (1-480).')
    
    def validate_price(self, price):
        try:
            price_val = float(price.data)
            if price_val < 0:
                raise ValueError
        except ValueError:
            raise ValidationError('Please enter a valid price.')

class AppointmentBookingForm(FlaskForm):
    stylist_id = SelectField('Stylist', coerce=int, validators=[DataRequired()])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    appointment_date = DateField('Date', validators=[DataRequired()])
    start_time = SelectField('Time', validators=[DataRequired()])
    customer_phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    customer_email = StringField('Email', validators=[Optional(), Email()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Book Appointment')
    
    def __init__(self, *args, **kwargs):
        super(AppointmentBookingForm, self).__init__(*args, **kwargs)
        # Populate stylist choices (only active stylists)
        from app.models import User, Role
        stylist_role = Role.query.filter_by(name='stylist').first()
        if stylist_role:
            stylists = User.query.join(User.roles).filter(
                User.is_active == True,
                User.roles.contains(stylist_role)
            ).all()
            self.stylist_id.choices = [(s.id, f"{s.first_name} {s.last_name}") for s in stylists]
        else:
            self.stylist_id.choices = []
        
        # Populate service choices (only active services)
        from app.models import Service
        services = Service.query.filter_by(is_active=True).all()
        self.service_id.choices = [(s.id, f"{s.name} (£{s.price}) - {s.duration}min") for s in services]
        
        # Populate time slots (9 AM to 6 PM, 30-minute intervals)
        time_slots = []
        for hour in range(9, 18):  # 9 AM to 6 PM
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                time_slots.append((time_str, time_str))
        self.start_time.choices = time_slots
    
    def validate_appointment_date(self, appointment_date):
        from datetime import date
        if appointment_date.data < date.today():
            raise ValidationError('Cannot book appointments in the past.')
    
    def validate_stylist_id(self, stylist_id):
        from app.models import User, Role
        stylist = User.query.get(stylist_id.data)
        if not stylist or not stylist.has_role('stylist'):
            raise ValidationError('Please select a valid stylist.')

class AppointmentManagementForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no-show', 'No Show')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Appointment')

class AppointmentFilterForm(FlaskForm):
    view_type = SelectField('View', choices=[
        ('week', 'Week View'),
        ('month', 'Month View')
    ], default='week', validators=[DataRequired()])
    stylist_id = SelectField('Stylist', coerce=int, validators=[Optional()])
    status = SelectField('Status', choices=[
        ('', 'All Statuses'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no-show', 'No Show')
    ], validators=[Optional()])
    submit = SubmitField('Filter')
    
    def __init__(self, *args, **kwargs):
        super(AppointmentFilterForm, self).__init__(*args, **kwargs)
        # Populate stylist choices (only active stylists)
        from app.models import User, Role
        stylist_role = Role.query.filter_by(name='stylist').first()
        if stylist_role:
            stylists = User.query.join(User.roles).filter(
                User.is_active == True,
                User.roles.contains(stylist_role)
            ).all()
            self.stylist_id.choices = [('', 'All Stylists')] + [(s.id, f"{s.first_name} {s.last_name}") for s in stylists]
        else:
            self.stylist_id.choices = [('', 'All Stylists')] 