import pytest
import json
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models import User, Role, EmploymentDetails
from app.forms import EmploymentDetailsForm

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
    """Create a stylist user for testing employment details."""
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

class TestEmploymentDetailsModel:
    """Test EmploymentDetails model functionality."""
    
    def test_employment_details_creation_employed(self, app, init_database, stylist_user):
        """Test creating employment details for employed staff."""
        with app.app_context():
            details = EmploymentDetails(
                user_id=stylist_user,
                employment_type='employed',
                commission_percentage=None,
                billing_method='salon_bills',
                job_role='Senior Stylist'
            )
            db.session.add(details)
            db.session.commit()
            
            assert details.id is not None
            assert details.user_id == stylist_user
            assert details.employment_type == 'employed'
            assert details.commission_percentage is None
            assert details.billing_method == 'salon_bills'
            assert details.job_role == 'Senior Stylist'
            assert details.is_employed == True
            assert details.is_self_employed == False
    
    def test_employment_details_creation_self_employed(self, app, init_database, stylist_user):
        """Test creating employment details for self-employed staff."""
        with app.app_context():
            details = EmploymentDetails(
                user_id=stylist_user,
                employment_type='self_employed',
                commission_percentage=Decimal('70.00'),
                billing_method='stylist_bills',
                job_role='Freelance Stylist'
            )
            db.session.add(details)
            db.session.commit()
            
            assert details.id is not None
            assert details.user_id == stylist_user
            assert details.employment_type == 'self_employed'
            assert details.commission_percentage == Decimal('70.00')
            assert details.billing_method == 'stylist_bills'
            assert details.job_role == 'Freelance Stylist'
            assert details.is_employed == False
            assert details.is_self_employed == True
    
    def test_unique_user_constraint(self, app, init_database, stylist_user):
        """Test that only one employment details record per user is allowed."""
        with app.app_context():
            # Create first employment details
            details1 = EmploymentDetails(
                user_id=stylist_user,
                employment_type='employed',
                billing_method='salon_bills',
                job_role='Stylist'
            )
            db.session.add(details1)
            db.session.commit()
            
            # Try to create second employment details for same user
            details2 = EmploymentDetails(
                user_id=stylist_user,
                employment_type='self_employed',
                commission_percentage=Decimal('80.00'),
                billing_method='stylist_bills',
                job_role='Freelance Stylist'
            )
            db.session.add(details2)
            
            # This should raise an integrity error
            with pytest.raises(Exception):
                db.session.commit()

class TestEmploymentDetailsForm:
    """Test EmploymentDetailsForm validation and functionality."""
    
    def test_valid_employed_form(self, app, init_database, stylist_user):
        """Test valid employment details form for employed staff."""
        with app.app_context():
            form_data = {
                'user_id': str(stylist_user),
                'employment_type': 'employed',
                'commission_percentage': '',
                'billing_method': 'salon_bills',
                'job_role': 'Senior Stylist'
            }
            
            form = EmploymentDetailsForm(data=form_data)
            assert form.validate() == True
    
    def test_valid_self_employed_form(self, app, init_database, stylist_user):
        """Test valid employment details form for self-employed staff."""
        with app.app_context():
            form_data = {
                'user_id': str(stylist_user),
                'employment_type': 'self_employed',
                'commission_percentage': '70.00',
                'billing_method': 'stylist_bills',
                'job_role': 'Freelance Stylist'
            }
            
            form = EmploymentDetailsForm(data=form_data)
            assert form.validate() == True
    
    def test_commission_required_for_self_employed(self, app, init_database, stylist_user):
        """Test that commission is required for self-employed staff."""
        with app.app_context():
            form_data = {
                'user_id': str(stylist_user),
                'employment_type': 'self_employed',
                'commission_percentage': '',  # Empty commission
                'billing_method': 'stylist_bills',
                'job_role': 'Freelance Stylist'
            }
            
            form = EmploymentDetailsForm(data=form_data)
            assert form.validate() == True  # Commission is optional in form
    
    def test_commission_not_allowed_for_employed(self, app, init_database, stylist_user):
        """Test that commission is not allowed for employed staff."""
        with app.app_context():
            form_data = {
                'user_id': str(stylist_user),
                'employment_type': 'employed',
                'commission_percentage': '70.00',  # Commission for employed
                'billing_method': 'salon_bills',
                'job_role': 'Stylist'
            }
            
            form = EmploymentDetailsForm(data=form_data)
            assert form.validate() == False
            assert 'commission_percentage' in str(form.errors)
    
    def test_invalid_commission_percentage(self, app, init_database, stylist_user):
        """Test validation of commission percentage range."""
        with app.app_context():
            form_data = {
                'user_id': str(stylist_user),
                'employment_type': 'self_employed',
                'commission_percentage': '150.00',  # Invalid percentage > 100
                'billing_method': 'stylist_bills',
                'job_role': 'Freelance Stylist'
            }
            
            form = EmploymentDetailsForm(data=form_data)
            assert form.validate() == False
            assert 'commission_percentage' in str(form.errors)
    
    def test_negative_commission_percentage(self, app, init_database, stylist_user):
        """Test validation of negative commission percentage."""
        with app.app_context():
            form_data = {
                'user_id': str(stylist_user),
                'employment_type': 'self_employed',
                'commission_percentage': '-10.00',  # Negative percentage
                'billing_method': 'stylist_bills',
                'job_role': 'Freelance Stylist'
            }
            
            form = EmploymentDetailsForm(data=form_data)
            assert form.validate() == False
            assert 'commission_percentage' in str(form.errors)
    
    def test_duplicate_user_validation(self, app, init_database, stylist_user):
        """Test that form prevents duplicate employment details for same user."""
        with app.app_context():
            # Create existing employment details
            existing_details = EmploymentDetails(
                user_id=stylist_user,
                employment_type='employed',
                billing_method='salon_bills',
                job_role='Stylist'
            )
            db.session.add(existing_details)
            db.session.commit()
            
            # Try to create new form for same user
            form_data = {
                'user_id': str(stylist_user),
                'employment_type': 'self_employed',
                'commission_percentage': '70.00',
                'billing_method': 'stylist_bills',
                'job_role': 'Freelance Stylist'
            }
            
            form = EmploymentDetailsForm(data=form_data)
            assert form.validate() == False
            assert 'user_id' in str(form.errors)

class TestEmploymentDetailsAdminRoutes:
    """Test employment details admin routes."""
    
    def test_employment_details_page_access_denied(self, client, init_database):
        """Test that employment details page requires authentication."""
        response = client.get('/admin/employment-details')
        assert response.status_code == 302  # Redirect to login
    
    def test_employment_details_page_requires_manager_role(self, client, init_database, manager_user):
        """Test that employment details page requires manager role."""
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        response = client.get('/admin/employment-details')
        assert response.status_code == 200
        assert b'Employment Details' in response.data
    
    def test_new_employment_details_page(self, client, init_database, manager_user, stylist_user):
        """Test new employment details page loads correctly."""
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        response = client.get('/admin/employment-details/new')
        assert response.status_code == 200
        assert b'New Employment Details' in response.data
    
    def test_create_employed_details(self, client, init_database, manager_user, stylist_user):
        """Test creating employment details for employed staff."""
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        # Submit form to create employed details
        response = client.post('/admin/employment-details/new', data={
            'user_id': str(stylist_user),
            'employment_type': 'employed',
            'commission_percentage': '',
            'billing_method': 'salon_bills',
            'job_role': 'Senior Stylist'
        })
        
        assert response.status_code == 302  # Redirect after successful creation
        
        # Verify details were created
        with client.application.app_context():
            details = EmploymentDetails.query.filter_by(user_id=stylist_user).first()
            assert details is not None
            assert details.employment_type == 'employed'
            assert details.commission_percentage is None
            assert details.billing_method == 'salon_bills'
            assert details.job_role == 'Senior Stylist'
    
    def test_create_self_employed_details(self, client, init_database, manager_user, stylist_user):
        """Test creating employment details for self-employed staff."""
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        # Submit form to create self-employed details
        response = client.post('/admin/employment-details/new', data={
            'user_id': str(stylist_user),
            'employment_type': 'self_employed',
            'commission_percentage': '70.00',
            'billing_method': 'stylist_bills',
            'job_role': 'Freelance Stylist'
        })
        
        assert response.status_code == 302  # Redirect after successful creation
        
        # Verify details were created
        with client.application.app_context():
            details = EmploymentDetails.query.filter_by(user_id=stylist_user).first()
            assert details is not None
            assert details.employment_type == 'self_employed'
            assert details.commission_percentage == Decimal('70.00')
            assert details.billing_method == 'stylist_bills'
            assert details.job_role == 'Freelance Stylist'
    
    def test_edit_employment_details(self, client, init_database, manager_user, stylist_user):
        """Test editing existing employment details."""
        # Create employment details first
        with client.application.app_context():
            details = EmploymentDetails(
                user_id=stylist_user,
                employment_type='employed',
                billing_method='salon_bills',
                job_role='Stylist'
            )
            db.session.add(details)
            db.session.commit()
            details_id = details.id
        
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        # Edit the details
        response = client.post(f'/admin/employment-details/{details_id}/edit', data={
            'user_id': str(stylist_user),
            'employment_type': 'self_employed',
            'commission_percentage': '75.00',
            'billing_method': 'stylist_bills',
            'job_role': 'Updated Freelance Stylist'
        })
        
        assert response.status_code == 302  # Redirect after successful update
        
        # Verify details were updated
        with client.application.app_context():
            details = EmploymentDetails.query.get(details_id)
            assert details.employment_type == 'self_employed'
            assert details.commission_percentage == Decimal('75.00')
            assert details.billing_method == 'stylist_bills'
            assert details.job_role == 'Updated Freelance Stylist'
    
    def test_delete_employment_details(self, client, init_database, manager_user, stylist_user):
        """Test deleting employment details."""
        # Create employment details first
        with client.application.app_context():
            details = EmploymentDetails(
                user_id=stylist_user,
                employment_type='employed',
                billing_method='salon_bills',
                job_role='Stylist to Delete'
            )
            db.session.add(details)
            db.session.commit()
            details_id = details.id
        
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        # Delete the details
        response = client.post(f'/admin/employment-details/{details_id}/delete')
        
        assert response.status_code == 302  # Redirect after successful deletion
        
        # Verify details were deleted
        with client.application.app_context():
            details = EmploymentDetails.query.get(details_id)
            assert details is None
    
    def test_employment_details_form_validation_error(self, client, init_database, manager_user, stylist_user):
        """Test employment details form validation error handling."""
        # Login as manager
        client.post('/auth/login', data={
            'username': 'manager',
            'password': 'managerpass123'
        })
        
        # Submit form with invalid data (commission for employed)
        response = client.post('/admin/employment-details/new', data={
            'user_id': str(stylist_user),
            'employment_type': 'employed',
            'commission_percentage': '70.00',  # Invalid for employed
            'billing_method': 'salon_bills',
            'job_role': 'Stylist'
        })
        
        assert response.status_code == 200  # Form should be re-displayed with errors
        # Form should be re-displayed with errors
        assert b'New Employment Details' in response.data 