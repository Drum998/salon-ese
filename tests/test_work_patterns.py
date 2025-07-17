import pytest
import json
from datetime import datetime, time
from app import create_app
from app.extensions import db
from app.models import User, Role, WorkPattern
from app.forms import WorkPatternForm

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
        return user.id

@pytest.fixture
def stylist_user(app, init_database):
    """Create a stylist user for testing work patterns."""
    with app.app_context():
        # Create stylist role if not exists
        stylist_role = Role.query.filter_by(name='stylist').first()
        if not stylist_role:
            stylist_role = Role(name='stylist', description='Test stylist role')
            db.session.add(stylist_role)
            db.session.commit()
        
        # Create stylist user
        user = User(
            username='stylist',
            email='stylist@example.com',
            first_name='Test',
            last_name='Stylist',
            is_active=True,
            email_verified=True
        )
        user.set_password('stylistpass123')
        user.roles.append(stylist_role)
        db.session.add(user)
        db.session.commit()
        return user.id

class TestWorkPatternModel:
    """Test WorkPattern model functionality."""
    
    def test_work_pattern_creation(self, app, init_database, stylist_user):
        """Test creating work pattern."""
        with app.app_context():
            work_schedule = {
                'monday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'tuesday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'wednesday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'thursday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'friday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'saturday': {'working': False, 'start': None, 'end': None},
                'sunday': {'working': False, 'start': None, 'end': None}
            }
            
            pattern = WorkPattern(
                user_id=stylist_user,
                pattern_name='Full Time Weekdays',
                work_schedule=work_schedule,
                is_active=True
            )
            db.session.add(pattern)
            db.session.commit()
            
            assert pattern.id is not None
            assert pattern.user_id == stylist_user
            assert pattern.pattern_name == 'Full Time Weekdays'
            assert pattern.is_active == True
            assert 'monday' in pattern.work_schedule
            assert pattern.work_schedule['monday']['working'] == True
            assert pattern.work_schedule['monday']['start'] == '09:00'
    
    def test_get_weekly_hours(self, app, init_database, stylist_user):
        """Test weekly hours calculation."""
        with app.app_context():
            work_schedule = {
                'monday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'tuesday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'wednesday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'thursday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'friday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'saturday': {'working': False, 'start': None, 'end': None},
                'sunday': {'working': False, 'start': None, 'end': None}
            }
            
            pattern = WorkPattern(
                user_id=stylist_user,
                pattern_name='Full Time Weekdays',
                work_schedule=work_schedule,
                is_active=True
            )
            db.session.add(pattern)
            db.session.commit()
            
            # 5 days * 8 hours = 40 hours
            assert pattern.get_weekly_hours() == 40
    
    def test_get_weekly_hours_partial_days(self, app, init_database, stylist_user):
        """Test weekly hours calculation with partial days."""
        with app.app_context():
            work_schedule = {
                'monday': {'working': True, 'start': '09:00', 'end': '13:00'},  # 4 hours
                'tuesday': {'working': True, 'start': '14:00', 'end': '18:00'},  # 4 hours
                'wednesday': {'working': False, 'start': None, 'end': None},
                'thursday': {'working': False, 'start': None, 'end': None},
                'friday': {'working': False, 'start': None, 'end': None},
                'saturday': {'working': False, 'start': None, 'end': None},
                'sunday': {'working': False, 'start': None, 'end': None}
            }
            
            pattern = WorkPattern(
                user_id=stylist_user,
                pattern_name='Part Time',
                work_schedule=work_schedule,
                is_active=True
            )
            db.session.add(pattern)
            db.session.commit()
            
            # 2 days * 4 hours = 8 hours
            assert pattern.get_weekly_hours() == 8
    
    def test_get_weekly_hours_no_working_days(self, app, init_database, stylist_user):
        """Test weekly hours calculation with no working days."""
        with app.app_context():
            work_schedule = {
                'monday': {'working': False, 'start': None, 'end': None},
                'tuesday': {'working': False, 'start': None, 'end': None},
                'wednesday': {'working': False, 'start': None, 'end': None},
                'thursday': {'working': False, 'start': None, 'end': None},
                'friday': {'working': False, 'start': None, 'end': None},
                'saturday': {'working': False, 'start': None, 'end': None},
                'sunday': {'working': False, 'start': None, 'end': None}
            }
            
            pattern = WorkPattern(
                user_id=stylist_user,
                pattern_name='No Work',
                work_schedule=work_schedule,
                is_active=True
            )
            db.session.add(pattern)
            db.session.commit()
            
            assert pattern.get_weekly_hours() == 0

class TestWorkPatternForm:
    """Test WorkPatternForm validation and functionality."""
    
    def test_valid_work_pattern_form(self, app, init_database, stylist_user):
        """Test valid work pattern form data."""
        with app.app_context():
            form_data = {
                'user_id': stylist_user,
                'pattern_name': 'Full Time Weekdays',
                'is_active': True,
                'monday_start': '09:00',
                'monday_end': '17:00',
                'monday_working': True,
                'tuesday_start': '09:00',
                'tuesday_end': '17:00',
                'tuesday_working': True,
                'wednesday_start': '09:00',
                'wednesday_end': '17:00',
                'wednesday_working': True,
                'thursday_start': '09:00',
                'thursday_end': '17:00',
                'thursday_working': True,
                'friday_start': '09:00',
                'friday_end': '17:00',
                'friday_working': True,
                'saturday_start': '',
                'saturday_end': '',
                'saturday_working': False,
                'sunday_start': '',
                'sunday_end': '',
                'sunday_working': False
            }
            
            form = WorkPatternForm(data=form_data)
            assert form.validate() == True
    
    def test_invalid_time_format(self, app, init_database, stylist_user):
        """Test form validation with invalid time format."""
        with app.app_context():
            form_data = {
                'user_id': stylist_user,
                'pattern_name': 'Test Pattern',
                'is_active': True,
                'monday_start': '25:00',  # Invalid time
                'monday_end': '17:00',
                'monday_working': True,
                'tuesday_start': '09:00',
                'tuesday_end': '17:00',
                'tuesday_working': True,
                'wednesday_start': '09:00',
                'wednesday_end': '17:00',
                'wednesday_working': True,
                'thursday_start': '09:00',
                'thursday_end': '17:00',
                'thursday_working': True,
                'friday_start': '09:00',
                'friday_end': '17:00',
                'friday_working': True,
                'saturday_start': '',
                'saturday_end': '',
                'saturday_working': False,
                'sunday_start': '',
                'sunday_end': '',
                'sunday_working': False
            }
            
            form = WorkPatternForm(data=form_data)
            assert form.validate() == False
            assert 'monday_start' in str(form.errors)
    
    def test_non_working_day_validation(self, app, init_database, stylist_user):
        """Test that non-working days don't require time validation."""
        with app.app_context():
            form_data = {
                'user_id': stylist_user,
                'pattern_name': 'Part Time',
                'is_active': True,
                'monday_start': '',  # Empty for non-working day
                'monday_end': '',  # Empty for non-working day
                'monday_working': False,  # Day is not working
                'tuesday_start': '09:00',
                'tuesday_end': '17:00',
                'tuesday_working': True,
                'wednesday_start': '09:00',
                'wednesday_end': '17:00',
                'wednesday_working': True,
                'thursday_start': '09:00',
                'thursday_end': '17:00',
                'thursday_working': True,
                'friday_start': '09:00',
                'friday_end': '17:00',
                'friday_working': True,
                'saturday_start': '',
                'saturday_end': '',
                'saturday_working': False,
                'sunday_start': '',
                'sunday_end': '',
                'sunday_working': False
            }
            
            form = WorkPatternForm(data=form_data)
            assert form.validate() == True
    
    def test_get_work_schedule_dict(self, app, init_database, stylist_user):
        """Test conversion of form data to work schedule dictionary."""
        with app.app_context():
            form_data = {
                'user_id': stylist_user,
                'pattern_name': 'Test Pattern',
                'is_active': True,
                'monday_start': '09:00',
                'monday_end': '17:00',
                'monday_working': True,
                'tuesday_start': '10:00',
                'tuesday_end': '18:00',
                'tuesday_working': True,
                'wednesday_start': '',
                'wednesday_end': '',
                'wednesday_working': False,
                'thursday_start': '09:00',
                'thursday_end': '17:00',
                'thursday_working': True,
                'friday_start': '09:00',
                'friday_end': '17:00',
                'friday_working': True,
                'saturday_start': '',
                'saturday_end': '',
                'saturday_working': False,
                'sunday_start': '',
                'sunday_end': '',
                'sunday_working': False
            }
            
            form = WorkPatternForm(data=form_data)
            schedule_dict = form.get_work_schedule_dict()
            
            assert schedule_dict['monday']['working'] == True
            assert schedule_dict['monday']['start'] == '09:00'
            assert schedule_dict['monday']['end'] == '17:00'
            
            assert schedule_dict['tuesday']['working'] == True
            assert schedule_dict['tuesday']['start'] == '10:00'
            assert schedule_dict['tuesday']['end'] == '18:00'
            
            assert schedule_dict['wednesday']['working'] == False
            assert schedule_dict['wednesday']['start'] is None
            assert schedule_dict['wednesday']['end'] is None

class TestWorkPatternAdminRoutes:
    """Test work patterns admin routes."""
    
    def test_work_patterns_page_access_denied(self, client, init_database):
        """Test that work patterns page requires authentication."""
        response = client.get('/admin/work-patterns')
        assert response.status_code == 302  # Redirect to login
    
    def test_work_patterns_page_requires_manager_role(self, client, init_database, manager_user):
        """Test that work patterns page requires manager role."""
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        response = client.get('/admin/work-patterns')
        assert response.status_code == 200
        assert b'Work Patterns' in response.data
    
    def test_new_work_pattern_page(self, client, init_database, manager_user, stylist_user):
        """Test new work pattern page loads correctly."""
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        response = client.get('/admin/work-patterns/new')
        assert response.status_code == 200
        assert b'New Work Pattern' in response.data
    
    def test_create_work_pattern(self, client, init_database, manager_user, stylist_user):
        """Test creating a new work pattern."""
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        # Submit form to create work pattern
        response = client.post('/admin/work-patterns/new', data={
            'user_id': stylist_user,
            'pattern_name': 'Full Time Weekdays',
            'is_active': True,
            'monday_start': '09:00',
            'monday_end': '17:00',
            'monday_working': True,
            'tuesday_start': '09:00',
            'tuesday_end': '17:00',
            'tuesday_working': True,
            'wednesday_start': '09:00',
            'wednesday_end': '17:00',
            'wednesday_working': True,
            'thursday_start': '09:00',
            'thursday_end': '17:00',
            'thursday_working': True,
            'friday_start': '09:00',
            'friday_end': '17:00',
            'friday_working': True,
            'saturday_start': '',
            'saturday_end': '',
            'saturday_working': False,
            'sunday_start': '',
            'sunday_end': '',
            'sunday_working': False
        })
        
        assert response.status_code == 302  # Redirect after successful creation
        
        # Verify pattern was created
        with client.application.app_context():
            pattern = WorkPattern.query.filter_by(pattern_name='Full Time Weekdays').first()
            assert pattern is not None
            assert pattern.user_id == stylist_user
            assert pattern.is_active == True
            assert pattern.work_schedule['monday']['working'] == True
            assert pattern.work_schedule['monday']['start'] == '09:00'
    
    def test_edit_work_pattern(self, client, init_database, manager_user, stylist_user):
        """Test editing an existing work pattern."""
        # Create a work pattern first
        with client.application.app_context():
            work_schedule = {
                'monday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'tuesday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'wednesday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'thursday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'friday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'saturday': {'working': False, 'start': None, 'end': None},
                'sunday': {'working': False, 'start': None, 'end': None}
            }
            
            pattern = WorkPattern(
                user_id=stylist_user,
                pattern_name='Original Pattern',
                work_schedule=work_schedule,
                is_active=True
            )
            db.session.add(pattern)
            db.session.commit()
            pattern_id = pattern.id
        
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        # Edit the pattern
        response = client.post(f'/admin/work-patterns/{pattern_id}/edit', data={
            'user_id': stylist_user,
            'pattern_name': 'Updated Pattern',
            'is_active': True,
            'monday_start': '10:00',
            'monday_end': '18:00',
            'monday_working': True,
            'tuesday_start': '10:00',
            'tuesday_end': '18:00',
            'tuesday_working': True,
            'wednesday_start': '10:00',
            'wednesday_end': '18:00',
            'wednesday_working': True,
            'thursday_start': '10:00',
            'thursday_end': '18:00',
            'thursday_working': True,
            'friday_start': '10:00',
            'friday_end': '18:00',
            'friday_working': True,
            'saturday_start': '',
            'saturday_end': '',
            'saturday_working': False,
            'sunday_start': '',
            'sunday_end': '',
            'sunday_working': False
        })
        
        assert response.status_code == 302  # Redirect after successful update
        
        # Verify pattern was updated
        with client.application.app_context():
            pattern = WorkPattern.query.get(pattern_id)
            assert pattern.pattern_name == 'Updated Pattern'
            assert pattern.work_schedule['monday']['start'] == '10:00'
            assert pattern.work_schedule['monday']['end'] == '18:00'
    
    def test_delete_work_pattern(self, client, init_database, manager_user, stylist_user):
        """Test deleting a work pattern."""
        # Create a work pattern first
        with client.application.app_context():
            work_schedule = {
                'monday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'tuesday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'wednesday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'thursday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'friday': {'working': True, 'start': '09:00', 'end': '17:00'},
                'saturday': {'working': False, 'start': None, 'end': None},
                'sunday': {'working': False, 'start': None, 'end': None}
            }
            
            pattern = WorkPattern(
                user_id=stylist_user,
                pattern_name='Pattern to Delete',
                work_schedule=work_schedule,
                is_active=True
            )
            db.session.add(pattern)
            db.session.commit()
            pattern_id = pattern.id
        
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        # Delete the pattern
        response = client.post(f'/admin/work-patterns/{pattern_id}/delete')
        
        assert response.status_code == 302  # Redirect after successful deletion
        
        # Verify pattern was deleted
        with client.application.app_context():
            pattern = WorkPattern.query.get(pattern_id)
            assert pattern is None
    
    def test_work_pattern_form_validation_error(self, client, init_database, manager_user, stylist_user):
        """Test work pattern form validation error handling."""
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        # Submit form with invalid time format
        response = client.post('/admin/work-patterns/new', data={
            'user_id': stylist_user,
            'pattern_name': 'Test Pattern',
            'is_active': True,
            'monday_start': '25:00',  # Invalid time
            'monday_end': '17:00',
            'monday_working': True,
            'tuesday_start': '09:00',
            'tuesday_end': '17:00',
            'tuesday_working': True,
            'wednesday_start': '09:00',
            'wednesday_end': '17:00',
            'wednesday_working': True,
            'thursday_start': '09:00',
            'thursday_end': '17:00',
            'thursday_working': True,
            'friday_start': '09:00',
            'friday_end': '17:00',
            'friday_working': True,
            'saturday_start': '',
            'saturday_end': '',
            'saturday_working': False,
            'sunday_start': '',
            'sunday_end': '',
            'sunday_working': False
        })
        
        assert response.status_code == 200  # Form should be re-displayed with errors
        # Form should be re-displayed with errors
        assert b'New Work Pattern' in response.data 