import pytest
from app import create_app
from app.extensions import db
from app.models import User, Role

@pytest.fixture
def app():
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

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

def test_register_page(client):
    """Test that registration page loads correctly."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Create Account' in response.data

def test_login_page(client):
    """Test that login page loads correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data

def test_user_registration(client, init_database):
    """Test user registration functionality."""
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'testpassword123',
        'password2': 'testpassword123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful' in response.data
    
    # Check that user was created
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'test@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'

def test_first_user_becomes_owner(client, init_database):
    """Test that the first registered user becomes owner."""
    response = client.post('/auth/register', data={
        'username': 'owner',
        'email': 'owner@example.com',
        'first_name': 'Owner',
        'last_name': 'User',
        'password': 'ownerpassword123',
        'password2': 'ownerpassword123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    with client.application.app_context():
        user = User.query.filter_by(username='owner').first()
        assert user is not None
        assert user.has_role('owner')
        assert user.email_verified == True

def test_user_login(client, init_database):
    """Test user login functionality."""
    # First register a user
    client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'testpassword123',
        'password2': 'testpassword123'
    })
    
    # Then try to login
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpassword123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Should redirect to dashboard after successful login
    assert b'Dashboard' in response.data or b'Welcome' in response.data

def test_invalid_login(client, init_database):
    """Test login with invalid credentials."""
    response = client.post('/auth/login', data={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data 