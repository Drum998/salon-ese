# Salon ESE - Hair Salon Management System

A comprehensive, role-based authentication and management system for hair salons, built with Flask and PostgreSQL. This system provides secure user management with multiple access levels, from guest users to salon owners.

## 🏗️ Architecture

### Technology Stack
- **Backend**: Flask 2.0.1 with SQLAlchemy ORM
- **Database**: PostgreSQL 13 (production) / SQLite (development)
- **Authentication**: Flask-Login with role-based access control
- **Forms**: Flask-WTF with CSRF protection
- **Containerization**: Docker with docker-compose
- **Testing**: pytest with coverage reporting

### System Architecture
```
salon-ese/
├── app/                    # Main application package
│   ├── models.py          # Database models (User, Role, UserProfile, LoginAttempt)
│   ├── forms.py           # WTForms for user input validation
│   ├── routes/            # Blueprint-based route handlers
│   │   ├── auth.py        # Authentication routes (login, register, logout)
│   │   ├── main.py        # Main application routes
│   │   ├── profile.py     # User profile management
│   │   └── admin.py       # Admin panel for user management
│   ├── templates/         # Jinja2 HTML templates
│   └── extensions.py      # Flask extensions initialization
├── config.py              # Configuration management
├── run.py                 # Application entry point
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container configuration
├── docker-compose.yml    # Multi-container orchestration
└── tests/                # Unit tests
```

## 👥 User Roles & Permissions

The system implements a hierarchical role-based access control system:

| Role | Level | Permissions |
|------|-------|-------------|
| **Guest** | 0 | View public pages, basic information |
| **Customer** | 1 | Book appointments, view personal profile |
| **Stylist** | 2 | Manage appointments, view customer profiles |
| **Manager** | 3 | Staff management, business reports |
| **Owner** | 4 | Full system access, user management |

### Role Hierarchy
- Each role inherits permissions from lower levels
- Access control is enforced at both route and template levels
- First registered user automatically becomes Owner

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Drum998/salon-ese.git
   cd salon-ese
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Web Interface: http://localhost:5010
   - Database: localhost:5432 (PostgreSQL)

4. **Create your first account**
   - Navigate to http://localhost:5010/auth/register
   - The first user registered will automatically be assigned the Owner role

### Development Setup

For local development without Docker:

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   ```bash
   export FLASK_ENV=development
   export FLASK_APP=run.py
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

## 📊 Database Models

### User Model
- Core user information (username, email, password)
- Role-based access control
- Account status and verification tracking

### Role Model
- Role definitions with permissions
- Hierarchical access levels
- JSON-based permission storage

### UserProfile Model
- Extended user information
- Stylist-specific fields (specialties, experience, certifications)
- Customer-specific fields (preferences, allergies, notes)

### LoginAttempt Model
- Security tracking for login attempts
- IP address and user agent logging
- Success/failure monitoring

## 🔐 Security Features

### Authentication & Authorization
- Secure password hashing with Werkzeug
- Session-based authentication with Flask-Login
- Role-based access control (RBAC)
- CSRF protection on all forms

### Security Monitoring
- Login attempt tracking
- IP address logging
- User agent tracking
- Failed login monitoring

### Data Protection
- Password hashing (bcrypt)
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Jinja2 auto-escaping)
- CSRF token validation

## 🧪 Testing

### Running Tests
```bash
# Run all tests
docker-compose exec web python -m pytest

# Run with coverage
docker-compose exec web python -m pytest --cov=app

# Run specific test file
docker-compose exec web python -m pytest tests/test_auth.py
```

### Test Structure
- Unit tests for models and forms
- Integration tests for authentication flows
- Coverage reporting for code quality

## 🐳 Docker Configuration

### Services
- **web**: Flask application (port 5010)
- **db**: PostgreSQL database (port 5432)

### Environment Variables
- `FLASK_ENV`: Application environment
- `DOCKER_ENV`: Docker environment flag
- `DATABASE_URL`: Database connection string

### Health Checks
- Database health monitoring
- Automatic retry logic for database initialization
- Graceful startup handling

## 🔧 Configuration

### Environment-Specific Settings
- **Development**: SQLite database, debug mode enabled
- **Production**: PostgreSQL database, security optimizations
- **Testing**: In-memory database, CSRF disabled

### Key Configuration Options
- Database connection strings
- Session lifetime settings
- File upload limits
- Email configuration (for future features)

## 📁 Project Structure

```
salon-ese/
├── app/                    # Application package
│   ├── __init__.py        # Application factory
│   ├── models.py          # Database models
│   ├── forms.py           # Form definitions
│   ├── extensions.py      # Flask extensions
│   ├── routes/            # Route blueprints
│   │   ├── __init__.py
│   │   ├── auth.py        # Authentication routes
│   │   ├── main.py        # Main routes
│   │   ├── profile.py     # Profile management
│   │   └── admin.py       # Admin panel
│   └── templates/         # HTML templates
│       ├── base.html      # Base template
│       ├── auth/          # Authentication templates
│       ├── main/          # Main page templates
│       ├── profile/       # Profile templates
│       └── admin/         # Admin templates
├── config.py              # Configuration classes
├── run.py                 # Application entry point
├── requirements.txt       # Dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Service orchestration
├── .gitignore           # Git ignore rules
├── pytest.ini          # Test configuration
├── test_db.py          # Database test script
├── test_models.py      # Model test script
└── README.md           # This file
```

## 🚀 Deployment

### Production Deployment
1. Set production environment variables
2. Configure PostgreSQL database
3. Set up reverse proxy (nginx)
4. Configure SSL certificates
5. Set up monitoring and logging

### Environment Variables
```bash
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the test files for usage examples

## 🔄 Version History

- **v1.0.0**: Initial release with role-based authentication system
  - User registration and login
  - Role-based access control
  - Admin panel for user management
  - Docker containerization
  - Comprehensive test suite

---

**Built with ❤️ for the salon management community** 