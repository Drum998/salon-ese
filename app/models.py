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

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='service', lazy='dynamic')
    
    def __repr__(self):
        return f'<Service {self.name}>'

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stylist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    
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
    
    def __repr__(self):
        return f'<Appointment {self.id}: {self.customer.first_name} with {self.stylist.first_name} on {self.appointment_date}>'
    
    @property
    def duration_minutes(self):
        """Calculate appointment duration in minutes"""
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