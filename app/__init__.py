from flask import Flask
from flask_migrate import Migrate
from config import config
from app.extensions import db, login_manager, migrate
from app.utils import to_uk_timezone, uk_timezone_strftime, from_json
import os
import time

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register template filters
    app.template_filter('uk_timezone')(to_uk_timezone)
    app.template_filter('uk_strftime')(uk_timezone_strftime)
    app.template_filter('from_json')(from_json)
    
    # Register blueprints
    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.profile import bp as profile_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.appointments import bp as appointments_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(appointments_bp, url_prefix='/appointments')
    
    # Create database tables and initialize roles
    with app.app_context():
        # Ensure instance folder exists
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass
        
        # Optimized database initialization with shorter retry times
        max_retries = 5  # Reduced from 10
        retry_delay = 2  # Reduced from 3
        
        for attempt in range(max_retries):
            try:
                print(f"Database initialization attempt {attempt + 1}/{max_retries}")
                
                # Create all tables
                db.create_all()
                print("✓ Tables created successfully")
                
                # Initialize default roles if they don't exist
                from app.models import Role
                default_roles = [
                    {'name': 'guest', 'description': 'Guest user with limited access'},
                    {'name': 'customer', 'description': 'Customer with booking access'},
                    {'name': 'stylist', 'description': 'Hair stylist with appointment management'},
                    {'name': 'manager', 'description': 'Manager with staff and business management'},
                    {'name': 'owner', 'description': 'Owner with full system access'}
                ]
                
                for role_data in default_roles:
                    role = Role.query.filter_by(name=role_data['name']).first()
                    if not role:
                        role = Role(**role_data)
                        db.session.add(role)
                        print(f"✓ Added role: {role_data['name']}")
                
                db.session.commit()
                print("✓ Database initialization completed successfully")
                break  # Success, exit retry loop
                
            except Exception as e:
                print(f"Database initialization attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.2, 10)  # Reduced max delay from 30 to 10 seconds
                else:
                    print(f"Database initialization failed after {max_retries} attempts: {e}")
                    # Don't raise the exception, just log it and continue
                    print("Continuing without database initialization...")
    
    return app 