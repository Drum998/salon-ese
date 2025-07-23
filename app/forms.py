from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField, TimeField, FieldList, FormField, IntegerField, HiddenField
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
    waiting_time = StringField('Waiting Time (minutes)', validators=[Optional()])
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
    
    def validate_waiting_time(self, waiting_time):
        if waiting_time.data:
            try:
                mins = int(waiting_time.data)
                if mins < 0 or mins > 240:  # Max 4 hours waiting time
                    raise ValueError
            except ValueError:
                raise ValidationError('Please enter a valid waiting time in minutes (0-240).')
    
    def validate_price(self, price):
        try:
            price_val = float(price.data)
            if price_val < 0:
                raise ValueError
        except ValueError:
            raise ValidationError('Please enter a valid price.')

class StylistServiceTimingForm(FlaskForm):
    """Form for managing stylist-specific service durations"""
    stylist_id = SelectField('Stylist', coerce=int, validators=[DataRequired()])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    custom_duration = StringField('Custom Duration (minutes)', validators=[DataRequired()])
    custom_waiting_time = StringField('Custom Waiting Time (minutes)', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    is_active = BooleanField('Active Timing', default=True)
    submit = SubmitField('Save Stylist Timing')
    
    def __init__(self, *args, **kwargs):
        super(StylistServiceTimingForm, self).__init__(*args, **kwargs)
        from app.models import User, Role, Service
        
        # Populate stylist choices
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
        services = Service.query.filter_by(is_active=True).all()
        self.service_id.choices = [(s.id, f"{s.name} (Standard: {s.duration}min)") for s in services]
        
        # Set default waiting time based on selected service if not already set
        if self.service_id.data and not self.custom_waiting_time.data:
            service = Service.query.get(self.service_id.data)
            if service and service.waiting_time:
                self.custom_waiting_time.data = str(service.waiting_time)
    
    def validate_custom_duration(self, custom_duration):
        try:
            mins = int(custom_duration.data)
            if mins <= 0 or mins > 480:  # Max 8 hours
                raise ValueError
        except ValueError:
            raise ValidationError('Please enter a valid duration in minutes (1-480).')
    
    def validate_custom_waiting_time(self, custom_waiting_time):
        if custom_waiting_time.data and custom_waiting_time.data.strip():
            try:
                mins = int(custom_waiting_time.data)
                if mins < 0 or mins > 240:  # Max 4 hours waiting time
                    raise ValueError
            except ValueError:
                raise ValidationError('Please enter a valid waiting time in minutes (0-240).')


class StylistServiceAssociationForm(FlaskForm):
    """Form for managing stylist-service associations"""
    stylist_id = SelectField('Stylist', validators=[DataRequired()])
    service_id = SelectField('Service', validators=[DataRequired()])
    is_allowed = BooleanField('Stylist can perform this service', default=True)
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Association')
    
    def validate_stylist_id(self, stylist_id):
        if not stylist_id.data or stylist_id.data == '':
            raise ValidationError('Please select a stylist.')
        try:
            int(stylist_id.data)
        except (ValueError, TypeError):
            raise ValidationError('Please select a valid stylist.')
    
    def validate_service_id(self, service_id):
        if not service_id.data or service_id.data == '':
            raise ValidationError('Please select a service.')
        try:
            int(service_id.data)
        except (ValueError, TypeError):
            raise ValidationError('Please select a valid service.')
    
    def __init__(self, *args, **kwargs):
        super(StylistServiceAssociationForm, self).__init__(*args, **kwargs)
        
        # Populate stylist choices (only stylists, managers, owners)
        from app.models import User, Role
        stylists = User.query.join(User.roles).filter(
            Role.name.in_(['stylist', 'manager', 'owner'])
        ).order_by(User.first_name, User.last_name).all()
        
        self.stylist_id.choices = [('', 'Select stylist')] + [
            (stylist.id, f"{stylist.first_name} {stylist.last_name} ({stylist.username})")
            for stylist in stylists
        ]
        
        # Populate service choices (only active services)
        from app.models import Service
        services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
        self.service_id.choices = [('', 'Select service')] + [
            (service.id, f"{service.name} ({service.duration}min - £{service.price})")
            for service in services
        ]


class AppointmentServiceForm(FlaskForm):
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    duration = IntegerField('Duration (minutes)', validators=[DataRequired()])
    waiting_time = IntegerField('Waiting Time (minutes)', validators=[Optional()])
    use_stylist_timing = BooleanField('Use Stylist Timing (if available)', default=False)
    
    def __init__(self, stylist_id=None, *args, **kwargs):
        super(AppointmentServiceForm, self).__init__(*args, **kwargs)
        self.stylist_id = stylist_id
        # Populate service choices (only active services)
        from app.models import Service, StylistServiceAssociation
        services = Service.query.filter_by(is_active=True).all()
        
        # If stylist_id is provided, filter services based on stylist associations
        if stylist_id:
            # Get services the stylist is allowed to perform
            allowed_services = StylistServiceAssociation.get_stylist_services(stylist_id)
            # If no associations exist, allow all services (backward compatibility)
            if not allowed_services:
                self.service_id.choices = [(s.id, f"{s.name} (£{s.price}) - {s.duration}min") for s in services]
            else:
                # Only show services the stylist is allowed to perform
                allowed_service_ids = [s.id for s in allowed_services]
                filtered_services = [s for s in services if s.id in allowed_service_ids]
                self.service_id.choices = [(s.id, f"{s.name} (£{s.price}) - {s.duration}min") for s in filtered_services]
        else:
            # No stylist selected, show all services
            self.service_id.choices = [(s.id, f"{s.name} (£{s.price}) - {s.duration}min") for s in services]
        
        # Set default duration and waiting time based on selected service
        if self.service_id.data:
            service = Service.query.get(self.service_id.data)
            if service:
                self.duration.data = service.duration
                self.waiting_time.data = service.waiting_time or 0
                
                # If stylist timing is enabled, check for custom timing
                if self.stylist_id and self.use_stylist_timing.data:
                    from app.models import StylistServiceTiming
                    custom_duration = StylistServiceTiming.get_stylist_duration(self.stylist_id, service.id)
                    custom_waiting_time = StylistServiceTiming.get_stylist_waiting_time(self.stylist_id, service.id)
                    
                    if custom_duration:
                        self.duration.data = custom_duration
                    if custom_waiting_time is not None:
                        self.waiting_time.data = custom_waiting_time

class AppointmentBookingForm(FlaskForm):
    stylist_id = SelectField('Stylist', coerce=int, validators=[DataRequired()])
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    services = FieldList(FormField(AppointmentServiceForm), min_entries=1, max_entries=10)
    appointment_date = DateField('Date', validators=[DataRequired()])
    start_time = SelectField('Time', validators=[DataRequired()])
    customer_phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    customer_email = StringField('Email', validators=[Optional(), Email()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Book Appointment')

    def __init__(self, *args, **kwargs):
        super(AppointmentBookingForm, self).__init__(*args, **kwargs)
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
        # Populate customer choices (all active users with 'customer' role)
        customer_role = Role.query.filter_by(name='customer').first()
        if customer_role:
            customers = User.query.join(User.roles).filter(
                User.is_active == True,
                User.roles.contains(customer_role)
            ).all()
            self.customer_id.choices = [(c.id, f"{c.first_name} {c.last_name} ({c.username})") for c in customers]
        else:
            self.customer_id.choices = []
        # If the current user is a customer, set their ID and hide the field
        from flask_login import current_user
        if current_user.is_authenticated and current_user.has_role('customer'):
            self.customer_id.choices = [(current_user.id, f"{current_user.first_name} {current_user.last_name} ({current_user.username})")]
            self.customer_id.data = current_user.id
            self.customer_id.widget = HiddenField().widget
        
        # Initialize service subforms with stylist timing support
        for service_form in self.services:
            service_form.stylist_id = self.stylist_id.data if self.stylist_id.data else None
        
        # Populate time slots (9 AM to 6 PM, 30-minute intervals)
        time_slots = []
        for hour in range(9, 18):
            for minute in [0, 30]:
                time_slots.append((f"{hour:02d}:{minute:02d}", f"{hour:02d}:{minute:02d}"))
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
    stylist_id = SelectField('Stylist', validators=[Optional()])
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
            self.stylist_id.choices = [('', 'All Stylists')] + [(str(s.id), f"{s.first_name} {s.last_name}") for s in stylists]
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
    monday_open = StringField('Monday Open', validators=[Optional()])
    monday_close = StringField('Monday Close', validators=[Optional()])
    monday_closed = BooleanField('Monday Closed')
    tuesday_open = StringField('Tuesday Open', validators=[Optional()])
    tuesday_close = StringField('Tuesday Close', validators=[Optional()])
    tuesday_closed = BooleanField('Tuesday Closed')
    wednesday_open = StringField('Wednesday Open', validators=[Optional()])
    wednesday_close = StringField('Wednesday Close', validators=[Optional()])
    wednesday_closed = BooleanField('Wednesday Closed')
    thursday_open = StringField('Thursday Open', validators=[Optional()])
    thursday_close = StringField('Thursday Close', validators=[Optional()])
    thursday_closed = BooleanField('Thursday Closed')
    friday_open = StringField('Friday Open', validators=[Optional()])
    friday_close = StringField('Friday Close', validators=[Optional()])
    friday_closed = BooleanField('Friday Closed')
    saturday_open = StringField('Saturday Open', validators=[Optional()])
    saturday_close = StringField('Saturday Close', validators=[Optional()])
    saturday_closed = BooleanField('Saturday Closed')
    sunday_open = StringField('Sunday Open', validators=[Optional()])
    sunday_close = StringField('Sunday Close', validators=[Optional()])
    sunday_closed = BooleanField('Sunday Closed')
    submit = SubmitField('Save Settings')

    def __init__(self, salon_settings=None, *args, **kwargs):
        super(SalonSettingsForm, self).__init__(*args, **kwargs)
        self.salon_settings = salon_settings
        
        if salon_settings:
            self.salon_name.data = salon_settings.salon_name
            self.emergency_extension_enabled.data = salon_settings.emergency_extension_enabled
            
            # Set opening hours from existing settings
            if salon_settings.opening_hours:
                for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                    day_data = salon_settings.opening_hours.get(day, {})
                    getattr(self, f'{day}_open').data = day_data.get('open', '')
                    getattr(self, f'{day}_close').data = day_data.get('close', '')
                    getattr(self, f'{day}_closed').data = day_data.get('closed', True)
        
        # If form data was provided, ensure boolean fields are properly set
        if 'data' in kwargs and kwargs['data']:
            data = kwargs['data']
            # Set boolean fields from form data
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                closed_key = f'{day}_closed'
                if closed_key in data:
                    # Convert string to boolean for form data
                    closed_value = data[closed_key]
                    if isinstance(closed_value, str):
                        closed_value = closed_value.lower() in ('true', '1', 'on', 'yes')
                    getattr(self, closed_key).data = closed_value

    def validate_time_format(self, time_str):
        if not time_str:
            return True
        try:
            hour, minute = map(int, time_str.split(':'))
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                return False
        except (ValueError, AttributeError):
            return False
        return True

    def validate_monday_open(self, field):
        if not getattr(self, 'monday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_monday_close(self, field):
        if not getattr(self, 'monday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_tuesday_open(self, field):
        if not getattr(self, 'tuesday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_tuesday_close(self, field):
        if not getattr(self, 'tuesday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_wednesday_open(self, field):
        if not getattr(self, 'wednesday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_wednesday_close(self, field):
        if not getattr(self, 'wednesday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_thursday_open(self, field):
        if not getattr(self, 'thursday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_thursday_close(self, field):
        if not getattr(self, 'thursday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_friday_open(self, field):
        if not getattr(self, 'friday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_friday_close(self, field):
        if not getattr(self, 'friday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_saturday_open(self, field):
        if not getattr(self, 'saturday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_saturday_close(self, field):
        if not getattr(self, 'saturday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_sunday_open(self, field):
        if not getattr(self, 'sunday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_sunday_close(self, field):
        if not getattr(self, 'sunday_closed').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')

    def validate(self):
        """Custom validation method to ensure all validators are called."""
        if not super().validate():
            return False
        
        # Call custom validators manually
        try:
            self.validate_monday_open(self.monday_open)
        except ValidationError as e:
            self.monday_open.errors.append(str(e))
            return False
        
        try:
            self.validate_monday_close(self.monday_close)
        except ValidationError as e:
            self.monday_close.errors.append(str(e))
            return False
        
        try:
            self.validate_tuesday_open(self.tuesday_open)
        except ValidationError as e:
            self.tuesday_open.errors.append(str(e))
            return False
        
        try:
            self.validate_tuesday_close(self.tuesday_close)
        except ValidationError as e:
            self.tuesday_close.errors.append(str(e))
            return False
        
        try:
            self.validate_wednesday_open(self.wednesday_open)
        except ValidationError as e:
            self.wednesday_open.errors.append(str(e))
            return False
        
        try:
            self.validate_wednesday_close(self.wednesday_close)
        except ValidationError as e:
            self.wednesday_close.errors.append(str(e))
            return False
        
        try:
            self.validate_thursday_open(self.thursday_open)
        except ValidationError as e:
            self.thursday_open.errors.append(str(e))
            return False
        
        try:
            self.validate_thursday_close(self.thursday_close)
        except ValidationError as e:
            self.thursday_close.errors.append(str(e))
            return False
        
        try:
            self.validate_friday_open(self.friday_open)
        except ValidationError as e:
            self.friday_open.errors.append(str(e))
            return False
        
        try:
            self.validate_friday_close(self.friday_close)
        except ValidationError as e:
            self.friday_close.errors.append(str(e))
            return False
        
        try:
            self.validate_saturday_open(self.saturday_open)
        except ValidationError as e:
            self.saturday_open.errors.append(str(e))
            return False
        
        try:
            self.validate_saturday_close(self.saturday_close)
        except ValidationError as e:
            self.saturday_close.errors.append(str(e))
            return False
        
        try:
            self.validate_sunday_open(self.sunday_open)
        except ValidationError as e:
            self.sunday_open.errors.append(str(e))
            return False
        
        try:
            self.validate_sunday_close(self.sunday_close)
        except ValidationError as e:
            self.sunday_close.errors.append(str(e))
            return False
        
        return True

    def get_opening_hours_dict(self):
        hours = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            open_field = getattr(self, f'{day}_open')
            close_field = getattr(self, f'{day}_close')
            closed_field = getattr(self, f'{day}_closed')
            hours[day] = {
                'open': open_field.data if open_field.data else None,
                'close': close_field.data if close_field.data else None,
                'closed': closed_field.data,
            }
        return hours

class WorkPatternForm(FlaskForm):
    user_id = SelectField('Staff Member', coerce=int, validators=[DataRequired()])
    pattern_name = StringField('Pattern Name', validators=[DataRequired(), Length(max=100)])
    is_active = BooleanField('Active Pattern', default=True)
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
        try:
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
        except Exception:
            self.user_id.choices = []
        if work_pattern:
            self.user_id.data = work_pattern.user_id
            self.pattern_name.data = work_pattern.pattern_name
            self.is_active.data = work_pattern.is_active
            
            # Set work schedule from existing pattern
            if work_pattern.work_schedule:
                for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                    day_data = work_pattern.work_schedule.get(day, {})
                    getattr(self, f'{day}_start').data = day_data.get('start', '')
                    getattr(self, f'{day}_end').data = day_data.get('end', '')
                    getattr(self, f'{day}_working').data = day_data.get('working', False)
        
        # If form data was provided, ensure boolean fields are properly set
        if 'data' in kwargs and kwargs['data']:
            data = kwargs['data']
            # Set boolean fields from form data
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                working_key = f'{day}_working'
                if working_key in data:
                    # Convert string to boolean for form data
                    working_value = data[working_key]
                    if isinstance(working_value, str):
                        working_value = working_value.lower() in ('true', '1', 'on', 'yes')
                    getattr(self, working_key).data = working_value

    def validate_time_format(self, time_str):
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
        if getattr(self, 'monday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_monday_end(self, field):
        if getattr(self, 'monday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_tuesday_start(self, field):
        if getattr(self, 'tuesday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_tuesday_end(self, field):
        if getattr(self, 'tuesday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_wednesday_start(self, field):
        if getattr(self, 'wednesday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_wednesday_end(self, field):
        if getattr(self, 'wednesday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_thursday_start(self, field):
        if getattr(self, 'thursday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_thursday_end(self, field):
        if getattr(self, 'thursday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_friday_start(self, field):
        if getattr(self, 'friday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_friday_end(self, field):
        if getattr(self, 'friday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_saturday_start(self, field):
        if getattr(self, 'saturday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_saturday_end(self, field):
        if getattr(self, 'saturday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_sunday_start(self, field):
        if getattr(self, 'sunday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')
    def validate_sunday_end(self, field):
        if getattr(self, 'sunday_working').data and field.data and not self.validate_time_format(field.data):
            raise ValidationError('Please enter a valid time in HH:MM format.')

    def validate(self):
        """Custom validation method to ensure all validators are called."""
        if not super().validate():
            return False
        
        # Call custom validators manually
        try:
            self.validate_monday_start(self.monday_start)
        except ValidationError as e:
            self.monday_start.errors.append(str(e))
            return False
        
        try:
            self.validate_monday_end(self.monday_end)
        except ValidationError as e:
            self.monday_end.errors.append(str(e))
            return False
        
        try:
            self.validate_tuesday_start(self.tuesday_start)
        except ValidationError as e:
            self.tuesday_start.errors.append(str(e))
            return False
        
        try:
            self.validate_tuesday_end(self.tuesday_end)
        except ValidationError as e:
            self.tuesday_end.errors.append(str(e))
            return False
        
        try:
            self.validate_wednesday_start(self.wednesday_start)
        except ValidationError as e:
            self.wednesday_start.errors.append(str(e))
            return False
        
        try:
            self.validate_wednesday_end(self.wednesday_end)
        except ValidationError as e:
            self.wednesday_end.errors.append(str(e))
            return False
        
        try:
            self.validate_thursday_start(self.thursday_start)
        except ValidationError as e:
            self.thursday_start.errors.append(str(e))
            return False
        
        try:
            self.validate_thursday_end(self.thursday_end)
        except ValidationError as e:
            self.thursday_end.errors.append(str(e))
            return False
        
        try:
            self.validate_friday_start(self.friday_start)
        except ValidationError as e:
            self.friday_start.errors.append(str(e))
            return False
        
        try:
            self.validate_friday_end(self.friday_end)
        except ValidationError as e:
            self.friday_end.errors.append(str(e))
            return False
        
        try:
            self.validate_saturday_start(self.saturday_start)
        except ValidationError as e:
            self.saturday_start.errors.append(str(e))
            return False
        
        try:
            self.validate_saturday_end(self.saturday_end)
        except ValidationError as e:
            self.saturday_end.errors.append(str(e))
            return False
        
        try:
            self.validate_sunday_start(self.sunday_start)
        except ValidationError as e:
            self.sunday_start.errors.append(str(e))
            return False
        
        try:
            self.validate_sunday_end(self.sunday_end)
        except ValidationError as e:
            self.sunday_end.errors.append(str(e))
            return False
        
        return True

    def get_work_schedule_dict(self):
        schedule = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            working_field = getattr(self, f'{day}_working')
            start_field = getattr(self, f'{day}_start')
            end_field = getattr(self, f'{day}_end')
            schedule[day] = {
                'working': working_field.data,
                'start': start_field.data if working_field.data and start_field.data else None,
                'end': end_field.data if working_field.data and end_field.data else None
            }
        return schedule

class AdminUserAddForm(FlaskForm):
    """Form for admin to add new users with role and employment assignment"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    role = SelectField('Role', choices=[
        ('customer', 'Customer'),
        ('stylist', 'Stylist'),
        ('manager', 'Manager'),
        ('owner', 'Owner')
    ], validators=[DataRequired()])
    employment_type = SelectField('Employment Type', choices=[
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed')
    ], validators=[Optional()])
    submit = SubmitField('Create User')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email address.')

class EmploymentDetailsForm(FlaskForm):
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
        try:
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
        except Exception:
            self.user_id.choices = []
        if employment_details:
            self.user_id.data = employment_details.user_id
            self.employment_type.data = employment_details.employment_type
            self.commission_percentage.data = str(employment_details.commission_percentage) if employment_details.commission_percentage else ''
            self.billing_method.data = employment_details.billing_method
            self.job_role.data = employment_details.job_role
        
        # If form data was provided, ensure employment_type is set for validation
        if 'data' in kwargs and kwargs['data']:
            self.employment_type.data = kwargs['data'].get('employment_type', self.employment_type.data)

    def validate_commission_percentage(self, field):
        employment_type = self.employment_type.data
        if employment_type == 'self_employed' and field.data:
            try:
                percentage = float(field.data)
                if percentage < 0 or percentage > 100:
                    raise ValueError
            except ValueError:
                raise ValidationError('Please enter a valid percentage between 0 and 100.')
        elif employment_type == 'employed' and field.data:
            raise ValidationError('Commission percentage is not applicable for employed staff.')

    def validate_user_id(self, field):
        try:
            from app.models import EmploymentDetails
            if self.employment_details and field.data == self.employment_details.user_id:
                return
            existing = EmploymentDetails.query.filter_by(user_id=field.data).first()
            if existing:
                raise ValidationError('This staff member already has employment details. Please edit the existing record.')
        except Exception as e:
            if "database" not in str(e).lower() and "connection" not in str(e).lower():
                raise

    def validate(self):
        """Custom validation method to ensure all validators are called."""
        if not super().validate():
            return False
        
        # Call custom validators manually
        try:
            self.validate_commission_percentage(self.commission_percentage)
        except ValidationError as e:
            self.commission_percentage.errors.append(str(e))
            return False
        
        try:
            self.validate_user_id(self.user_id)
        except ValidationError as e:
            self.user_id.errors.append(str(e))
            return False
        
        return True 