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

class WorkPatternForm(FlaskForm):
    """Form for managing staff work patterns"""
    user_id = SelectField('Staff Member', coerce=int, validators=[DataRequired()])
    pattern_name = StringField('Pattern Name', validators=[DataRequired(), Length(max=100)])
    is_active = BooleanField('Active Pattern', default=True)
    
    # Work schedule for each day
    monday_start = StringField('Monday Start', validators=[Optional()])
    monday_end = StringField('Monday End', validators=[Optional()])
    monday_working = BooleanField('Monday Working')
    
    tuesday_start = StringField('Tuesday Start', validators=[Optional()])
    tuesday_end = StringField('Tuesday End', validators=[Optional()])
    tuesday_working = BooleanField('Tuesday Working')
    
    wednesday_start = StringField('Wednesday Start', validators=[Optional()])
    wednesday_end = StringField('Wednesday End', validators=[Optional()])
    wednesday_working = BooleanField('Wednesday Working')
    
    thursday_start = StringField('Thursday Start', validators=[Optional()])
    thursday_end = StringField('Thursday End', validators=[Optional()])
    thursday_working = BooleanField('Thursday Working')
    
    friday_start = StringField('Friday Start', validators=[Optional()])
    friday_end = StringField('Friday End', validators=[Optional()])
    friday_working = BooleanField('Friday Working')
    
    saturday_start = StringField('Saturday Start', validators=[Optional()])
    saturday_end = StringField('Saturday End', validators=[Optional()])
    saturday_working = BooleanField('Saturday Working')
    
    sunday_start = StringField('Sunday Start', validators=[Optional()])
    sunday_end = StringField('Sunday End', validators=[Optional()])
    sunday_working = BooleanField('Sunday Working')
    
    submit = SubmitField('Save Work Pattern')
    
    def __init__(self, work_pattern=None, *args, **kwargs):
        super(WorkPatternForm, self).__init__(*args, **kwargs)
        self.work_pattern = work_pattern
        
        # Populate staff member choices (only stylists and managers)
        from app.models import User, Role
        stylist_role = Role.query.filter_by(name='stylist').first()
        manager_role = Role.query.filter_by(name='manager').first()
        
        if stylist_role and manager_role:
            staff = User.query.join(User.roles).filter(
                User.is_active == True,
                User.roles.contains(stylist_role) | User.roles.contains(manager_role)
            ).all()
            self.user_id.choices = [(s.id, f"{s.first_name} {s.last_name} ({s.username})") for s in staff]
        else:
            self.user_id.choices = []
        
        # Pre-populate form if editing existing pattern
        if work_pattern:
            self.user_id.data = work_pattern.user_id
            self.pattern_name.data = work_pattern.pattern_name
            self.is_active.data = work_pattern.is_active
            
            if work_pattern.work_schedule:
                schedule = work_pattern.work_schedule
                for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                    if day in schedule:
                        day_data = schedule[day]
                        setattr(self, f'{day}_working', day_data.get('working', False))
                        setattr(self, f'{day}_start', day_data.get('start', ''))
                        setattr(self, f'{day}_end', day_data.get('end', ''))
    
    def validate_time_format(self, time_str):
        """Validate time format (HH:MM)"""
        if not time_str:
            return True
        try:
            hour, minute = map(int, time_str.split(':'))
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                return False
        except (ValueError, AttributeError):
            return False
        return True
    
    def validate_monday_start(self, field):
        if self.monday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def validate_monday_end(self, field):
        if self.monday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def validate_tuesday_start(self, field):
        if self.tuesday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def validate_tuesday_end(self, field):
        if self.tuesday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def validate_wednesday_start(self, field):
        if self.wednesday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def validate_wednesday_end(self, field):
        if self.wednesday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def validate_thursday_start(self, field):
        if self.thursday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def validate_thursday_end(self, field):
        if self.thursday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def validate_friday_start(self, field):
        if self.friday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def validate_friday_end(self, field):
        if self.friday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def validate_saturday_start(self, field):
        if self.saturday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def validate_saturday_end(self, field):
        if self.saturday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def validate_sunday_start(self, field):
        if self.sunday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def validate_sunday_end(self, field):
        if self.sunday_working.data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    
    def get_work_schedule_dict(self):
        """Convert form data to work schedule dictionary"""
        schedule = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            working = getattr(self, f'{day}_working').data
            start = getattr(self, f'{day}_start').data
            end = getattr(self, f'{day}_end').data
            
            schedule[day] = {
                'working': working,
                'start': start if working and start else None,
                'end': end if working and end else None
            }
        
        return schedule

class EmploymentDetailsForm(FlaskForm):
    """Form for managing employment details"""
    user_id = SelectField('Staff Member', coerce=int, validators=[DataRequired()])
    employment_type = SelectField('Employment Type', choices=[
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed')
    ], validators=[DataRequired()])
    commission_percentage = StringField('Commission Percentage (%)', validators=[Optional()])
    billing_method = SelectField('Billing Method', choices=[
        ('salon_bills', 'Salon Bills'),
        ('stylist_bills', 'Stylist Bills')
    ], validators=[DataRequired()])
    job_role = StringField('Job Role', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Save Employment Details')
    
    def __init__(self, employment_details=None, *args, **kwargs):
        super(EmploymentDetailsForm, self).__init__(*args, **kwargs)
        self.employment_details = employment_details
        
        # Populate staff member choices (only stylists and managers)
        from app.models import User, Role
        stylist_role = Role.query.filter_by(name='stylist').first()
        manager_role = Role.query.filter_by(name='manager').first()
        
        if stylist_role and manager_role:
            staff = User.query.join(User.roles).filter(
                User.is_active == True,
                User.roles.contains(stylist_role) | User.roles.contains(manager_role)
            ).all()
            self.user_id.choices = [(s.id, f"{s.first_name} {s.last_name} ({s.username})") for s in staff]
        else:
            self.user_id.choices = []
        
        # Pre-populate form if editing existing details
        if employment_details:
            self.user_id.data = employment_details.user_id
            self.employment_type.data = employment_details.employment_type
            self.commission_percentage.data = str(employment_details.commission_percentage) if employment_details.commission_percentage else ''
            self.billing_method.data = employment_details.billing_method
            self.job_role.data = employment_details.job_role
    
    def validate_commission_percentage(self, field):
        """Validate commission percentage for self-employed staff"""
        if self.employment_type.data == 'self_employed' and field.data:
            try:
                percentage = float(field.data)
                if percentage < 0 or percentage > 100:
                    raise ValueError
            except ValueError:
                raise ValidationError('Please enter a valid percentage between 0 and 100.')
        elif self.employment_type.data == 'employed' and field.data:
            raise ValidationError('Commission percentage is not applicable for employed staff.')
    
    def validate_user_id(self, field):
        """Ensure user doesn't already have employment details"""
        from app.models import EmploymentDetails
        if self.employment_details and field.data == self.employment_details.user_id:
            return
        
        existing = EmploymentDetails.query.filter_by(user_id=field.data).first()
        if existing:
            raise ValidationError('This staff member already has employment details. Please edit the existing record.') 