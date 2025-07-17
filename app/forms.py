from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField, TimeField
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
        # Populate stylist choices
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

# ============================================================================
# NEW FORMS FOR SALON MANAGEMENT
# ============================================================================

class SalonSettingsForm(FlaskForm):
    """Form for managing salon settings and opening hours"""
    salon_name = StringField('Salon Name', validators=[DataRequired(), Length(max=100)])
    emergency_extension_enabled = BooleanField('Enable Emergency Hour Extensions', default=True)
    
    # Opening hours for each day
    monday_open = StringField('Monday Open', validators=[DataRequired()])
    monday_close = StringField('Monday Close', validators=[DataRequired()])
    monday_closed = BooleanField('Monday Closed')
    
    tuesday_open = StringField('Tuesday Open', validators=[DataRequired()])
    tuesday_close = StringField('Tuesday Close', validators=[DataRequired()])
    tuesday_closed = BooleanField('Tuesday Closed')
    
    wednesday_open = StringField('Wednesday Open', validators=[DataRequired()])
    wednesday_close = StringField('Wednesday Close', validators=[DataRequired()])
    wednesday_closed = BooleanField('Wednesday Closed')
    
    thursday_open = StringField('Thursday Open', validators=[DataRequired()])
    thursday_close = StringField('Thursday Close', validators=[DataRequired()])
    thursday_closed = BooleanField('Thursday Closed')
    
    friday_open = StringField('Friday Open', validators=[DataRequired()])
    friday_close = StringField('Friday Close', validators=[DataRequired()])
    friday_closed = BooleanField('Friday Closed')
    
    saturday_open = StringField('Saturday Open', validators=[DataRequired()])
    saturday_close = StringField('Saturday Close', validators=[DataRequired()])
    saturday_closed = BooleanField('Saturday Closed')
    
    sunday_open = StringField('Sunday Open', validators=[DataRequired()])
    sunday_close = StringField('Sunday Close', validators=[DataRequired()])
    sunday_closed = BooleanField('Sunday Closed')
    
    submit = SubmitField('Save Settings')
    
    def __init__(self, salon_settings=None, *args, **kwargs):
        super(SalonSettingsForm, self).__init__(*args, **kwargs)
        self.salon_settings = salon_settings
        
        # Pre-populate form with existing settings
        if salon_settings and salon_settings.opening_hours:
            hours = salon_settings.opening_hours
            
            # Set salon name
            if salon_settings.salon_name:
                self.salon_name.data = salon_settings.salon_name
            
            # Set emergency extension setting
            self.emergency_extension_enabled.data = salon_settings.emergency_extension_enabled
            
            # Set opening hours for each day
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                day_data = hours.get(day, {})
                open_field = getattr(self, f'{day}_open')
                close_field = getattr(self, f'{day}_close')
                closed_field = getattr(self, f'{day}_closed')
                
                open_field.data = day_data.get('open', '09:00')
                close_field.data = day_data.get('close', '18:00')
                closed_field.data = day_data.get('closed', False)
    
    def validate_time_format(self, time_str):
        """Validate time format (HH:MM)"""
        try:
            hour, minute = map(int, time_str.split(':'))
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                raise ValueError
        except (ValueError, AttributeError):
            raise ValidationError('Time must be in HH:MM format (e.g., 09:00)')
    
    def validate_monday_open(self, field):
        if not self.monday_closed.data:
            self.validate_time_format(field.data)
    
    def validate_monday_close(self, field):
        if not self.monday_closed.data:
            self.validate_time_format(field.data)
    
    def validate_tuesday_open(self, field):
        if not self.tuesday_closed.data:
            self.validate_time_format(field.data)
    
    def validate_tuesday_close(self, field):
        if not self.tuesday_closed.data:
            self.validate_time_format(field.data)
    
    def validate_wednesday_open(self, field):
        if not self.wednesday_closed.data:
            self.validate_time_format(field.data)
    
    def validate_wednesday_close(self, field):
        if not self.wednesday_closed.data:
            self.validate_time_format(field.data)
    
    def validate_thursday_open(self, field):
        if not self.thursday_closed.data:
            self.validate_time_format(field.data)
    
    def validate_thursday_close(self, field):
        if not self.thursday_closed.data:
            self.validate_time_format(field.data)
    
    def validate_friday_open(self, field):
        if not self.friday_closed.data:
            self.validate_time_format(field.data)
    
    def validate_friday_close(self, field):
        if not self.friday_closed.data:
            self.validate_time_format(field.data)
    
    def validate_saturday_open(self, field):
        if not self.saturday_closed.data:
            self.validate_time_format(field.data)
    
    def validate_saturday_close(self, field):
        if not self.saturday_closed.data:
            self.validate_time_format(field.data)
    
    def validate_sunday_open(self, field):
        if not self.sunday_closed.data:
            self.validate_time_format(field.data)
    
    def validate_sunday_close(self, field):
        if not self.sunday_closed.data:
            self.validate_time_format(field.data)
    
    def get_opening_hours_dict(self):
        """Convert form data to opening hours dictionary"""
        hours = {}
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            closed_field = getattr(self, f'{day}_closed')
            open_field = getattr(self, f'{day}_open')
            close_field = getattr(self, f'{day}_close')
            
            hours[day] = {
                'closed': closed_field.data,
                'open': open_field.data if not closed_field.data else '09:00',
                'close': close_field.data if not closed_field.data else '18:00'
            }
        return hours 