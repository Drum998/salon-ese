import pytest
import json
from datetime import datetime, time
from app import create_app
from app.extensions import db
from app.models import User, Role, SalonSettings
from app.forms import SalonSettingsForm

@pytest.fixture
def app():
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    with app.app_context():
        db.create_all()
        
        # Create test roles
        roles = ['guest', 'customer', 'stylist', 'manager', 'owner']
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=f'Test {role_name} role')
                db.session.add(role)
        
        db.session.commit()
        yield db
        db.drop_all()

@pytest.fixture
def manager_user(app, init_database):
    """Create a manager user for testing admin routes."""
    with app.app_context():
        # Create manager role if not exists
        manager_role = Role.query.filter_by(name='manager').first()
        if not manager_role:
            manager_role = Role(name='manager', description='Test manager role')
            db.session.add(manager_role)
            db.session.commit()
        
        # Create manager user
        user = User(
            username='manager',
            email='manager@example.com',
            first_name='Test',
            last_name='Manager',
            is_active=True,
            email_verified=True
        )
        user.set_password('managerpass123')
        user.roles.append(manager_role)
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def default_salon_settings(app, init_database):
    """Create default salon settings for testing."""
    with app.app_context():
        settings = SalonSettings.get_settings()
        return settings

class TestSalonSettingsModel:
    """Test SalonSettings model functionality."""
    
    def test_salon_settings_creation(self, app, init_database):
        """Test creating salon settings."""
        with app.app_context():
            settings = SalonSettings(
                salon_name='Test Salon',
                opening_hours={
                    'monday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'tuesday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'wednesday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'thursday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'friday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'saturday': {'open': '09:00', 'close': '17:00', 'closed': False},
                    'sunday': {'open': '09:00', 'close': '17:00', 'closed': True}
                },
                emergency_extension_enabled=True
            )
            db.session.add(settings)
            db.session.commit()
            
            assert settings.id is not None
            assert settings.salon_name == 'Test Salon'
            assert settings.emergency_extension_enabled == True
            assert 'monday' in settings.opening_hours
            assert settings.opening_hours['monday']['open'] == '09:00'
    
    def test_get_settings_creates_default(self, app, init_database):
        """Test that get_settings creates default settings if none exist."""
        with app.app_context():
            # Ensure no settings exist
            db.session.query(SalonSettings).delete()
            db.session.commit()
            
            settings = SalonSettings.get_settings()
            assert settings is not None
            assert settings.salon_name == 'Salon ESE'
            assert settings.emergency_extension_enabled == True
            assert 'monday' in settings.opening_hours
    
    def test_get_settings_returns_existing(self, app, init_database):
        """Test that get_settings returns existing settings."""
        with app.app_context():
            # Create custom settings
            custom_settings = SalonSettings(
                salon_name='Custom Salon',
                opening_hours={'monday': {'open': '10:00', 'close': '19:00', 'closed': False}},
                emergency_extension_enabled=False
            )
            db.session.add(custom_settings)
            db.session.commit()
            
            settings = SalonSettings.get_settings()
            assert settings.salon_name == 'Custom Salon'
            assert settings.emergency_extension_enabled == False
            assert settings.opening_hours['monday']['open'] == '10:00'

class TestSalonSettingsForm:
    """Test SalonSettingsForm validation and functionality."""
    
    def test_valid_salon_settings_form(self, app, init_database):
        """Test valid salon settings form data."""
        with app.app_context():
            form_data = {
                'salon_name': 'Test Salon',
                'emergency_extension_enabled': True,
                'monday_open': '09:00',
                'monday_close': '18:00',
                'monday_closed': False,
                'tuesday_open': '09:00',
                'tuesday_close': '18:00',
                'tuesday_closed': False,
                'wednesday_open': '09:00',
                'wednesday_close': '18:00',
                'wednesday_closed': False,
                'thursday_open': '09:00',
                'thursday_close': '18:00',
                'thursday_closed': False,
                'friday_open': '09:00',
                'friday_close': '18:00',
                'friday_closed': False,
                'saturday_open': '09:00',
                'saturday_close': '17:00',
                'saturday_closed': False,
                'sunday_open': '09:00',
                'sunday_close': '17:00',
                'sunday_closed': True
            }
            
            form = SalonSettingsForm(data=form_data)
            assert form.validate() == True
    
    def test_invalid_time_format(self, app, init_database):
        """Test form validation with invalid time format."""
        with app.app_context():
            form_data = {
                'salon_name': 'Test Salon',
                'emergency_extension_enabled': True,
                'monday_open': '25:00',  # Invalid time
                'monday_close': '18:00',
                'monday_closed': False,
                'tuesday_open': '09:00',
                'tuesday_close': '18:00',
                'tuesday_closed': False,
                'wednesday_open': '09:00',
                'wednesday_close': '18:00',
                'wednesday_closed': False,
                'thursday_open': '09:00',
                'thursday_close': '18:00',
                'thursday_closed': False,
                'friday_open': '09:00',
                'friday_close': '18:00',
                'friday_closed': False,
                'saturday_open': '09:00',
                'saturday_close': '17:00',
                'saturday_closed': False,
                'sunday_open': '09:00',
                'sunday_close': '17:00',
                'sunday_closed': True
            }
            
            form = SalonSettingsForm(data=form_data)
            assert form.validate() == False
            assert 'monday_open' in str(form.errors)
    
    def test_closed_day_validation(self, app, init_database):
        """Test that closed days don't require time validation."""
        with app.app_context():
            form_data = {
                'salon_name': 'Test Salon',
                'emergency_extension_enabled': True,
                'monday_open': '',  # Empty for closed day
                'monday_close': '',  # Empty for closed day
                'monday_closed': True,  # Day is closed
                'tuesday_open': '09:00',
                'tuesday_close': '18:00',
                'tuesday_closed': False,
                'wednesday_open': '09:00',
                'wednesday_close': '18:00',
                'wednesday_closed': False,
                'thursday_open': '09:00',
                'thursday_close': '18:00',
                'thursday_closed': False,
                'friday_open': '09:00',
                'friday_close': '18:00',
                'friday_closed': False,
                'saturday_open': '09:00',
                'saturday_close': '17:00',
                'saturday_closed': False,
                'sunday_open': '09:00',
                'sunday_close': '17:00',
                'sunday_closed': True
            }
            
            form = SalonSettingsForm(data=form_data)
            assert form.validate() == True
    
    def test_get_opening_hours_dict(self, app, init_database):
        """Test conversion of form data to opening hours dictionary."""
        with app.app_context():
            form_data = {
                'salon_name': 'Test Salon',
                'emergency_extension_enabled': True,
                'monday_open': '09:00',
                'monday_close': '18:00',
                'monday_closed': False,
                'tuesday_open': '10:00',
                'tuesday_close': '19:00',
                'tuesday_closed': False,
                'wednesday_open': '',
                'wednesday_close': '',
                'wednesday_closed': True,
                'thursday_open': '09:00',
                'thursday_close': '18:00',
                'thursday_closed': False,
                'friday_open': '09:00',
                'friday_close': '18:00',
                'friday_closed': False,
                'saturday_open': '09:00',
                'saturday_close': '17:00',
                'saturday_closed': False,
                'sunday_open': '09:00',
                'sunday_close': '17:00',
                'sunday_closed': True
            }
            
            form = SalonSettingsForm(data=form_data)
            hours_dict = form.get_opening_hours_dict()
            
            assert hours_dict['monday']['open'] == '09:00'
            assert hours_dict['monday']['close'] == '18:00'
            assert hours_dict['monday']['closed'] == False
            
            assert hours_dict['tuesday']['open'] == '10:00'
            assert hours_dict['tuesday']['close'] == '19:00'
            assert hours_dict['tuesday']['closed'] == False
            
            assert hours_dict['wednesday']['closed'] == True
            assert hours_dict['wednesday']['open'] is None
            assert hours_dict['wednesday']['close'] is None

class TestSalonSettingsAdminRoutes:
    """Test salon settings admin routes."""
    
    def test_salon_settings_page_access_denied(self, client, init_database):
        """Test that salon settings page requires authentication."""
        response = client.get('/admin/salon-settings')
        assert response.status_code == 302  # Redirect to login
    
    def test_salon_settings_page_requires_manager_role(self, client, init_database, manager_user):
        """Test that salon settings page requires manager role."""
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        response = client.get('/admin/salon-settings')
        assert response.status_code == 200
        assert b'Salon Settings' in response.data
    
    def test_salon_settings_form_submission(self, client, init_database, manager_user):
        """Test salon settings form submission."""
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        # Submit form with new settings
        response = client.post('/admin/salon-settings', data={
            'salon_name': 'Updated Salon Name',
            'emergency_extension_enabled': 'on',
            'monday_open': '10:00',
            'monday_close': '19:00',
            'monday_closed': '',
            'tuesday_open': '10:00',
            'tuesday_close': '19:00',
            'tuesday_closed': '',
            'wednesday_open': '10:00',
            'wednesday_close': '19:00',
            'wednesday_closed': '',
            'thursday_open': '10:00',
            'thursday_close': '19:00',
            'thursday_closed': '',
            'friday_open': '10:00',
            'friday_close': '19:00',
            'friday_closed': '',
            'saturday_open': '09:00',
            'saturday_close': '17:00',
            'saturday_closed': '',
            'sunday_open': '09:00',
            'sunday_close': '17:00',
            'sunday_closed': 'on'
        })
        
        assert response.status_code == 302  # Redirect after successful update
        
        # Verify settings were saved
        with client.application.app_context():
            settings = SalonSettings.get_settings()
            assert settings.salon_name == 'Updated Salon Name'
            assert settings.opening_hours['monday']['open'] == '10:00'
            assert settings.opening_hours['monday']['close'] == '19:00'
    
    def test_salon_settings_form_validation_error(self, client, init_database, manager_user):
        """Test salon settings form validation error handling."""
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        # Submit form with invalid time format
        response = client.post('/admin/salon-settings', data={
            'salon_name': 'Test Salon',
            'emergency_extension_enabled': 'on',
            'monday_open': '25:00',  # Invalid time
            'monday_close': '18:00',
            'monday_closed': '',
            'tuesday_open': '09:00',
            'tuesday_close': '18:00',
            'tuesday_closed': '',
            'wednesday_open': '09:00',
            'wednesday_close': '18:00',
            'wednesday_closed': '',
            'thursday_open': '09:00',
            'thursday_close': '18:00',
            'thursday_closed': '',
            'friday_open': '09:00',
            'friday_close': '18:00',
            'friday_closed': '',
            'saturday_open': '09:00',
            'saturday_close': '17:00',
            'saturday_closed': '',
            'sunday_open': '09:00',
            'sunday_close': '17:00',
            'sunday_closed': 'on'
        })
        
        assert response.status_code == 200  # Form should be re-displayed with errors
        # Form should be re-displayed with errors
        assert b'Salon Settings' in response.data 