from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db
from app.utils import uk_utcnow
from config import Config

# Association table for many-to-many relationship between users and roles
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=uk_utcnow)
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.Text)  # JSON string of permissions
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    roles = db.relationship('Role', 
                          secondary=user_roles,
                          backref=db.backref('users', lazy='dynamic'))
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)
    
    def has_permission(self, permission):
        for role in self.roles:
            if role.permissions and permission in role.permissions:
                return True
        return False
    
    def get_highest_role_level(self):
        if not self.roles:
            return 0
        return max(Config.ROLES.get(role.name, 0) for role in self.roles)
    
    def can_access(self, required_role):
        user_level = self.get_highest_role_level()
        required_level = Config.ROLES.get(required_role, 0)
        return user_level >= required_level
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bio = db.Column(db.Text)
    profile_image = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    
    # Stylist-specific fields
    specialties = db.Column(db.Text)  # JSON string of specialties
    experience_years = db.Column(db.Integer)
    certifications = db.Column(db.Text)  # JSON string of certifications
    availability = db.Column(db.Text)  # JSON string of availability schedule
    
    # Customer-specific fields
    preferred_stylist_id = db.Column(db.Integer)  # Store as integer, not foreign key
    hair_type = db.Column(db.String(50))
    allergies = db.Column(db.Text)  # JSON string of allergies
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    def __repr__(self):
        return f'<UserProfile {self.user_id}>'

class LoginAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    success = db.Column(db.Boolean, default=False)
    attempted_at = db.Column(db.DateTime, default=uk_utcnow)
    
    def __repr__(self):
        return f'<LoginAttempt {self.user_id} - {"Success" if self.success else "Failed"}>'

class AppointmentService(db.Model):
    __tablename__ = 'appointment_service'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes (can be custom)
    waiting_time = db.Column(db.Integer)  # Optional waiting/processing time in minutes
    order = db.Column(db.Integer, nullable=False, default=0)  # Sequence/order of service in appointment

    # Relationships
    appointment = db.relationship('Appointment', back_populates='services_link')
    service = db.relationship('Service', back_populates='appointments_link')

    def __repr__(self):
        return f'<AppointmentService {self.appointment_id} - {self.service_id}>'

# Update Service model
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False)  # Standard duration in minutes
    waiting_time = db.Column(db.Integer)  # Optional waiting/processing time in minutes
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=uk_utcnow)

    # Relationships
    appointments = db.relationship('Appointment', backref='service', lazy='dynamic')  # Deprecated
    appointments_link = db.relationship('AppointmentService', back_populates='service', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Service {self.name}>'

class StylistServiceTiming(db.Model):
    """Stylist-specific timing for services"""
    id = db.Column(db.Integer, primary_key=True)
    stylist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    custom_duration = db.Column(db.Integer, nullable=False)  # Custom duration in minutes
    custom_waiting_time = db.Column(db.Integer)  # Custom waiting time in minutes (optional)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    # Relationships
    stylist = db.relationship('User', foreign_keys=[stylist_id], backref='service_timings')
    service = db.relationship('Service', backref='stylist_timings')
    
    # Unique constraint to prevent duplicate stylist-service combinations
    __table_args__ = (db.UniqueConstraint('stylist_id', 'service_id', name='_stylist_service_uc'),)
    
    def __repr__(self):
        return f'<StylistServiceTiming {self.stylist_id}-{self.service_id}>'
    
    @classmethod
    def get_stylist_duration(cls, stylist_id, service_id):
        """Get custom duration for a stylist-service combination, or None if not set"""
        timing = cls.query.filter_by(
            stylist_id=stylist_id,
            service_id=service_id,
            is_active=True
        ).first()
        return timing.custom_duration if timing else None
    
    @classmethod
    def get_stylist_waiting_time(cls, stylist_id, service_id):
        """Get custom waiting time for a stylist-service combination, or None if not set"""
        timing = cls.query.filter_by(
            stylist_id=stylist_id,
            service_id=service_id,
            is_active=True
        ).first()
        return timing.custom_waiting_time if timing else None


class StylistServiceAssociation(db.Model):
    """Association table for stylist-service permissions"""
    id = db.Column(db.Integer, primary_key=True)
    stylist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    is_allowed = db.Column(db.Boolean, default=True)  # Whether stylist can perform this service
    notes = db.Column(db.Text)  # Optional notes about the association
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    # Relationships
    stylist = db.relationship('User', foreign_keys=[stylist_id], backref='service_associations')
    service = db.relationship('Service', backref='stylist_associations')
    
    # Unique constraint to prevent duplicate stylist-service combinations
    __table_args__ = (db.UniqueConstraint('stylist_id', 'service_id', name='_stylist_service_assoc_uc'),)
    
    def __repr__(self):
        return f'<StylistServiceAssociation {self.stylist_id}:{self.service_id} (allowed: {self.is_allowed})>'
    
    @classmethod
    def can_stylist_perform_service(cls, stylist_id, service_id):
        """Check if a stylist is allowed to perform a specific service"""
        association = cls.query.filter_by(
            stylist_id=stylist_id,
            service_id=service_id
        ).first()
        
        # If no association exists, default to allowed (backward compatibility)
        if association is None:
            return True
        
        return association.is_allowed
    
    @classmethod
    def get_stylist_services(cls, stylist_id):
        """Get all services a stylist is allowed to perform"""
        associations = cls.query.filter_by(
            stylist_id=stylist_id,
            is_allowed=True
        ).all()
        return [assoc.service for assoc in associations]
    
    @classmethod
    def get_service_stylists(cls, service_id):
        """Get all stylists who can perform a specific service"""
        associations = cls.query.filter_by(
            service_id=service_id,
            is_allowed=True
        ).all()
        return [assoc.stylist for assoc in associations]


# Update Appointment model
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stylist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)  # Deprecated, keep for migration
    booked_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Who booked the appointment

    # Appointment details
    appointment_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    # Contact and notes
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(120))
    notes = db.Column(db.Text)

    # Status and tracking
    status = db.Column(db.String(20), default='confirmed')  # confirmed, completed, cancelled, no-show
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)

    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='customer_appointments')
    stylist = db.relationship('User', foreign_keys=[stylist_id], backref='stylist_appointments')
    booked_by = db.relationship('User', foreign_keys=[booked_by_id], backref='booked_appointments')
    services_link = db.relationship('AppointmentService', back_populates='appointment', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Appointment {self.id}: {self.customer.first_name} with {self.stylist.first_name} on {self.appointment_date}>'

    @property
    def duration_minutes(self):
        """Calculate total appointment duration in minutes (sum of all services)"""
        if self.services_link:
            return sum(link.duration + (link.waiting_time or 0) for link in self.services_link)
        if self.start_time and self.end_time:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            return end_minutes - start_minutes
        return 0
    
    @property
    def is_past(self):
        """Check if appointment is in the past"""
        from datetime import datetime, date
        today = date.today()
        now = datetime.now().time()
        
        if self.appointment_date < today:
            return True
        elif self.appointment_date == today and self.end_time < now:
            return True
        return False
    
    @property
    def is_today(self):
        """Check if appointment is today"""
        from datetime import date
        return self.appointment_date == date.today()
    
    @property
    def is_upcoming(self):
        """Check if appointment is in the future"""
        return not self.is_past

class AppointmentStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # confirmed, completed, cancelled, no-show
    notes = db.Column(db.Text)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=uk_utcnow)
    
    # Relationships
    appointment = db.relationship('Appointment', backref='status_history')
    changed_by = db.relationship('User', backref='appointment_status_changes')
    
    def __repr__(self):
        return f'<AppointmentStatus {self.appointment_id}: {self.status}>'

# ============================================================================
# NEW MODELS FOR CLIENT REQUIREMENTS
# ============================================================================

class SalonSettings(db.Model):
    """Salon configuration settings including opening hours"""
    id = db.Column(db.Integer, primary_key=True)
    salon_name = db.Column(db.String(100), nullable=False, default='Salon ESE')
    opening_hours = db.Column(db.JSON, nullable=False)  # Store daily opening/closing times
    emergency_extension_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    def __repr__(self):
        return f'<SalonSettings {self.salon_name}>'
    
    @classmethod
    def get_settings(cls):
        """Get the salon settings, create default if none exist"""
        settings = cls.query.first()
        if not settings:
            # Create default settings
            default_hours = {
                'monday': {'open': '09:00', 'close': '18:00', 'closed': False},
                'tuesday': {'open': '09:00', 'close': '18:00', 'closed': False},
                'wednesday': {'open': '09:00', 'close': '18:00', 'closed': False},
                'thursday': {'open': '09:00', 'close': '18:00', 'closed': False},
                'friday': {'open': '09:00', 'close': '18:00', 'closed': False},
                'saturday': {'open': '09:00', 'close': '17:00', 'closed': False},
                'sunday': {'open': '10:00', 'close': '16:00', 'closed': True}
            }
            settings = cls(opening_hours=default_hours)
            db.session.add(settings)
            db.session.commit()
        return settings

class WorkPattern(db.Model):
    """Staff work patterns and schedules"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pattern_name = db.Column(db.String(100), nullable=False)
    work_schedule = db.Column(db.JSON, nullable=False)  # Store weekly work schedule
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    # Relationships
    user = db.relationship('User', backref='work_patterns')
    
    def __repr__(self):
        return f'<WorkPattern {self.pattern_name} for {self.user.username}>'
    
    def get_weekly_hours(self):
        """Calculate total weekly hours from work schedule"""
        total_hours = 0
        for day, schedule in self.work_schedule.items():
            if schedule.get('working', False):
                start_time = schedule.get('start')
                end_time = schedule.get('end')
                
                # Skip if times are None or empty
                if not start_time or not end_time:
                    continue
                
                # Parse times and calculate hours
                start_hour, start_minute = map(int, start_time.split(':'))
                end_hour, end_minute = map(int, end_time.split(':'))
                
                start_minutes = start_hour * 60 + start_minute
                end_minutes = end_hour * 60 + end_minute
                
                total_hours += (end_minutes - start_minutes) / 60
        
        return round(total_hours, 2)

class EmploymentDetails(db.Model):
    """Employment details for staff members"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    employment_type = db.Column(db.String(20), nullable=False)  # 'employed' or 'self_employed'
    commission_percentage = db.Column(db.Numeric(5, 2))  # For self-employed (e.g., 70.00 for 70%)
    billing_method = db.Column(db.String(20), default='salon_bills')  # 'salon_bills' or 'stylist_bills'
    job_role = db.Column(db.String(100))
    
    # HR System Integration - New Fields
    start_date = db.Column(db.Date, nullable=False, default=datetime.now().date())
    end_date = db.Column(db.Date, nullable=True)  # Null for current employees
    hourly_rate = db.Column(db.Numeric(8, 2), nullable=True)  # For employed staff
    commission_rate = db.Column(db.Numeric(5, 2), nullable=True)  # For self-employed (e.g., 70.00 for 70%)
    base_salary = db.Column(db.Numeric(10, 2), nullable=True)  # For employed staff
    
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    # Relationships
    user = db.relationship('User', backref='employment_details', uselist=False)
    
    def __repr__(self):
        return f'<EmploymentDetails {self.user_id}>'
    
    @property
    def is_self_employed(self):
        return self.employment_type == 'self_employed'
    
    @property
    def is_employed(self):
        return self.employment_type == 'employed'
    
    # HR System Integration - New Methods
    def calculate_hourly_cost(self, hours):
        """Calculate cost for hourly employees"""
        if not self.is_employed or not self.hourly_rate:
            return 0
        return float(self.hourly_rate) * hours
    
    def calculate_commission_cost(self, service_revenue):
        """Calculate cost for commission-based employees"""
        if not self.is_self_employed or not self.commission_rate:
            return 0
        return float(service_revenue) * (float(self.commission_rate) / 100)
    
    def is_currently_employed(self):
        """Check if employee is currently employed"""
        if self.end_date is None:
            return True
        return self.end_date >= datetime.now().date()
    
    def get_current_rate(self):
        """Get current rate (hourly or commission)"""
        if self.is_employed:
            return self.hourly_rate
        else:
            return self.commission_rate

class HolidayQuota(db.Model):
    """Holiday entitlements and usage tracking"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_hours_per_week = db.Column(db.Integer, nullable=False)
    holiday_days_entitled = db.Column(db.Integer, nullable=False)
    holiday_days_taken = db.Column(db.Integer, default=0)
    holiday_days_remaining = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    # Relationships
    user = db.relationship('User', backref='holiday_quotas')
    
    def __repr__(self):
        return f'<HolidayQuota {self.user.username} {self.year}: {self.holiday_days_remaining} days remaining>'
    
    @classmethod
    def calculate_entitlement(cls, hours_per_week):
        """
        Calculate holiday entitlement based on UK employment law
        Standard: 5.6 weeks per year (28 days for full-time)
        """
        if hours_per_week >= 37.5:  # Full-time
            return 28
        elif hours_per_week >= 20:  # Part-time
            return int((hours_per_week / 37.5) * 28)
        else:  # Reduced hours
            return int((hours_per_week / 37.5) * 28)
    
    def update_remaining_days(self):
        """Update remaining days based on taken days"""
        self.holiday_days_remaining = self.holiday_days_entitled - self.holiday_days_taken

class HolidayRequest(db.Model):
    """Holiday requests and approvals"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='holiday_requests')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approved_holidays')
    
    def __repr__(self):
        return f'<HolidayRequest {self.user.username} {self.start_date} to {self.end_date} - {self.status}>'
    
    @property
    def is_approved(self):
        """Check if holiday request is approved"""
        return self.status == 'approved'
    
    @property
    def is_pending(self):
        """Check if holiday request is pending"""
        return self.status == 'pending'
    
    @property
    def is_rejected(self):
        """Check if holiday request is rejected"""
        return self.status == 'rejected'
    
    def approve(self, approved_by_user):
        """Approve the holiday request"""
        self.status = 'approved'
        self.approved_by_id = approved_by_user.id
        self.approved_at = uk_utcnow()
        
        # Update holiday quota
        quota = HolidayQuota.query.filter_by(
            user_id=self.user_id, 
            year=self.start_date.year
        ).first()
        
        if quota:
            quota.holiday_days_taken += self.days_requested
            quota.update_remaining_days()
    
    def reject(self, rejected_by_user, notes=None):
        """Reject the holiday request"""
        self.status = 'rejected'
        self.approved_by_id = rejected_by_user.id
        self.approved_at = uk_utcnow()
        if notes:
            self.notes = notes

class BillingElement(db.Model):
    """Salon billing elements for commission calculations"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., 'color', 'electric'
    percentage = db.Column(db.Numeric(5, 2), nullable=False)  # e.g., 25.00 for 25%
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    def __repr__(self):
        return f'<BillingElement {self.name}>'
    
    @classmethod
    def get_active_elements(cls):
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def get_total_percentage(cls):
        elements = cls.get_active_elements()
        return sum(float(element.percentage) for element in elements)

class AppointmentCost(db.Model):
    """Track cost calculations for each appointment"""
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    stylist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Cost breakdown
    service_revenue = db.Column(db.Numeric(10, 2), nullable=False)  # Total service price
    stylist_cost = db.Column(db.Numeric(10, 2), nullable=False)  # Cost to salon for stylist
    salon_profit = db.Column(db.Numeric(10, 2), nullable=False)  # Salon's profit
    
    # Calculation details
    calculation_method = db.Column(db.String(20), nullable=False)  # 'hourly' or 'commission'
    hours_worked = db.Column(db.Numeric(4, 2), nullable=True)  # For hourly calculations
    commission_amount = db.Column(db.Numeric(10, 2), nullable=True)  # For commission calculations
    
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    # Relationships
    appointment = db.relationship('Appointment', backref='cost_details')
    stylist = db.relationship('User', foreign_keys=[stylist_id])
    
    def __repr__(self):
        return f'<AppointmentCost {self.appointment_id} - {self.stylist_id}>'
    
    @property
    def profit_margin_percentage(self):
        """Calculate profit margin as percentage"""
        if self.service_revenue == 0:
            return 0
        return (float(self.salon_profit) / float(self.service_revenue)) * 100 