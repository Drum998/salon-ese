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