# Salon ESE - Development Guide

## 🎯 **Overview**

This guide provides comprehensive development documentation for the Salon ESE project, including setup, architecture, API documentation, testing, and development workflow.

## 🏗️ **Architecture**

### **Technology Stack**
- **Backend**: Flask 2.0.1 with SQLAlchemy ORM
- **Database**: PostgreSQL 13 (production) / SQLite (development)
- **Authentication**: Flask-Login with role-based access control
- **Forms**: Flask-WTF with CSRF protection
- **Containerization**: Docker with docker-compose
- **Testing**: pytest with coverage reporting
- **Timezone**: pytz for UK timezone support (BST/GMT)
- **UI**: Modern sidebar navigation with responsive design

### **Key Models**
```python
# Core Models
User, Role, Service, Appointment, AppointmentStatus
SalonSettings, WorkPattern, EmploymentDetails
HolidayQuota, HolidayRequest, BillingElement
StylistServiceAssociation, StylistServiceTiming
```

### **Role-Based Access Control**
- **Guest**: Limited access to public pages
- **Customer**: Book appointments, view own appointments
- **Stylist**: View own appointments, manage personal schedule
- **Manager**: Full appointment management, staff oversight
- **Owner**: Complete system access, financial management

## 🔧 **Development Setup**

### **Prerequisites**
- Python 3.9+
- Docker and Docker Compose
- Git

### **Local Development Setup**

```bash
# Clone the repository
git clone https://github.com/Drum998/salon-ese.git
cd salon-ese

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=development
export FLASK_APP=run.py

# Run the application
python run.py
```

### **Docker Development Setup**

```bash
# Clone the repository
git clone https://github.com/Drum998/salon-ese.git
cd salon-ese

# Start the application
docker-compose up --build

# Access the application
# Web: http://localhost:5010
# Database: localhost:5432
```

## 📁 **Project Structure**

```
salon-ese/
├── app/                    # Main application package
│   ├── __init__.py        # Application factory
│   ├── models.py          # Database models
│   ├── forms.py           # Form definitions
│   ├── extensions.py      # Flask extensions
│   ├── utils.py           # Utility functions
│   ├── routes/            # Route modules
│   │   ├── admin.py       # Admin routes
│   │   ├── auth.py        # Authentication routes
│   │   ├── appointments.py # Appointment routes
│   │   └── main.py        # Main routes
│   ├── services/          # Business logic services
│   │   ├── hr_service.py  # HR calculations
│   │   ├── analytics_service.py # Analytics
│   │   └── holiday_service.py # Holiday management
│   ├── templates/         # Jinja2 templates
│   └── static/            # Static files (CSS, JS, images)
├── tests/                 # Test files
├── migrations/            # Database migrations
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker configuration
├── Dockerfile            # Docker image definition
└── run.py                # Application entry point
```

## 🔌 **API Documentation**

### **Base URL**
- **Development**: `http://localhost:5010`
- **Production**: `https://your-domain.com`

### **Authentication Endpoints**

#### **User Registration**
**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "confirm_password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

**Response:**
- **Success (302)**: Redirects to login page
- **Error (400)**: Validation errors in form

#### **User Login**
**POST** `/auth/login`

Authenticate user and create session.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securepassword123",
  "remember_me": true
}
```

**Response:**
- **Success (302)**: Redirects to dashboard or next page
- **Error (400)**: Invalid credentials

#### **User Logout**
**GET** `/auth/logout`

Terminate user session.

**Response:**
- **Success (302)**: Redirects to home page
- **Requires**: Authentication

### **Profile Management Endpoints**

#### **View Profile**
**GET** `/profile`

Display user's profile information.

**Response:**
- **Success (200)**: Profile page with user data
- **Requires**: Authentication

#### **Edit Profile**
**GET/POST** `/profile/edit`

Update user profile information.

**Request Body (POST):**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "bio": "Professional hair stylist with 5 years experience",
  "date_of_birth": "1990-01-01",
  "address": "123 Main St, City, State 12345",
  "emergency_contact": "Jane Doe",
  "emergency_phone": "+1234567890"
}
```

### **Appointment Endpoints**

#### **View Appointments**
**GET** `/appointments`

View user's appointments.

**Query Parameters:**
- `status`: Filter by status (confirmed, completed, cancelled)
- `date_from`: Start date filter
- `date_to`: End date filter

**Response:**
- **Success (200)**: Appointments list page
- **Requires**: Authentication

#### **Book Appointment**
**GET/POST** `/appointments/book`

Book a new appointment.

**Request Body (POST):**
```json
{
  "stylist_id": 1,
  "service_id": 2,
  "appointment_date": "2024-01-15",
  "start_time": "14:00",
  "customer_phone": "+1234567890",
  "customer_email": "customer@example.com",
  "notes": "Special styling request"
}
```

**Response:**
- **Success (302)**: Redirects to appointment confirmation
- **Error (400)**: Validation errors

### **Admin Endpoints**

#### **Admin Dashboard**
**GET** `/admin/dashboard`

Admin dashboard with system overview.

**Response:**
- **Success (200)**: Admin dashboard page
- **Requires**: Manager/Owner role

#### **User Management**
**GET** `/admin/users`

View and manage users.

**Response:**
- **Success (200)**: Users management page
- **Requires**: Manager/Owner role

#### **HR Dashboard**
**GET** `/admin/hr-dashboard`

HR dashboard with financial overview.

**Response:**
- **Success (200)**: HR dashboard page
- **Requires**: Manager/Owner role

## 🧪 **Testing Guide**

### **Comprehensive Test Runner**

The Salon ESE project includes a comprehensive test runner system that organizes and executes all tests efficiently.

#### **Quick Start**

```bash
# Run all tests
./run_tests_docker.sh

# Run smoke tests (quick validation)
./run_tests_docker.sh smoke

# Run development tests
./run_tests_docker.sh dev

# Run production tests
./run_tests_docker.sh prod

# Run specific category
./run_tests_docker.sh core
./run_tests_docker.sh hr
./run_tests_docker.sh ui
```

#### **Test Categories**

##### **Core Tests**
- **Description**: Core system functionality tests
- **Tests**: Database connectivity, models, authentication, timezone handling
- **Files**: `test_db.py`, `test_models.py`, `test_new_models.py`, `test_template_filter.py`, `test_timezone.py`, `test_auth.py`

##### **Admin Tests**
- **Description**: Admin panel and user management tests
- **Tests**: Admin functionality, user management, role management
- **Files**: `test_admin.py`, `tests/test_auth.py`

##### **HR Tests**
- **Description**: HR system and employment management tests
- **Tests**: HR functionality, commission calculations, employment details, work patterns
- **Files**: `test_hr_system.py`, `test_commission_system.py`, `test_analytics_system.py`, `tests/test_salon_settings.py`, `tests/test_work_patterns.py`, `tests/test_employment_details.py`

##### **UI Tests**
- **Description**: User interface and navigation tests
- **Tests**: Navigation, calendar views, appointment display, services matrix
- **Files**: `test_sidebar_navigation.py`, `test_services_matrix.py`, `test_single_block_css.py`, `test_calendar_navigation.py`, `test_calendar_view.py`, `test_click_to_book.py`, `test_appointment_visibility.py`, `test_appointment_display.py`

##### **Analytics Tests**
- **Description**: Analytics and reporting system tests
- **Tests**: Analytics functionality, commission analytics, reporting
- **Files**: `test_analytics_system.py`, `test_commission_system.py`

##### **Integration Tests**
- **Description**: Integration and system-wide tests
- **Tests**: System integration, salon hours integration, debug tests
- **Files**: `test_salon_hours_integration.py`, `debug_tests.py`

#### **Test Presets**

##### **Smoke Tests**
- **Purpose**: Quick validation of basic functionality
- **Use Case**: Fast feedback during development
- **Tests**: Database connectivity, authentication, admin functionality, basic settings

##### **Development Tests**
- **Purpose**: Comprehensive testing during active development
- **Use Case**: Daily development workflow
- **Tests**: Core functionality, admin features, HR system, basic UI

##### **Production Tests**
- **Purpose**: Full system validation before deployment
- **Use Case**: Pre-deployment verification
- **Tests**: All system components, integration tests, performance validation

#### **Configuration**

Tests can be configured in `test_config.py`:

```python
# Enable/disable individual tests by commenting them out
CORE_TESTS = [
    'test_db.py',                      # Database connectivity tests
    # 'test_new_models.py',            # Temporarily disabled
    'test_auth.py',                    # Authentication tests
]

# Test execution settings
TEST_SETTINGS = {
    'timeout_per_test': 300,           # 5 minutes per test
    'timeout_pytest': 600,             # 10 minutes for pytest
    'run_pytest_coverage': True,       # Run pytest with coverage
    'show_detailed_output': True,      # Show detailed test output
    'stop_on_first_failure': False,    # Continue running tests even if one fails
}
```

### **Individual Test Files**

#### **Salon Settings Tests (`tests/test_salon_settings.py`)**
Tests for salon configuration and opening hours management.

**Model Tests:**
- Creation with valid data
- Default settings creation when none exist
- Existing settings retrieval and caching behavior

**Form Tests:**
- HH:MM format validation for opening/closing times
- Business logic validation for closed days
- Form data to opening hours dictionary conversion
- Error handling for invalid time formats

**Route Tests:**
- Authentication and authorization verification
- CRUD operations (Create, read, update)
- Form validation error display

#### **Work Patterns Tests (`tests/test_work_patterns.py`)**
Tests for staff work schedules and pattern management.

**Model Tests:**
- Work pattern creation with weekly schedules
- Automatic weekly hours computation
- Edge cases for partial days and various schedules

**Form Tests:**
- Time format and schedule validation
- Business logic for non-working days
- Form data to work schedule dictionary conversion
- Staff member dropdown population

**Route Tests:**
- Authentication and authorization
- Full CRUD operations
- Form validation and database error handling

#### **Employment Details Tests (`tests/test_employment_details.py`)**
Tests for employment type and commission management.

**Model Tests:**
- Both employed and self-employed scenarios
- Unique user constraint enforcement
- Employment type boolean properties
- Decimal precision for commission percentages

**Form Tests:**
- Commission percentage range validation (0-100)
- Business logic for commission-only self-employed staff
- Duplicate user prevention
- Proper decimal handling

**Route Tests:**
- Authentication and authorization
- Full CRUD operations
- Form validation and constraint violations

## 🔄 **Development Workflow**

### **Development Phases**

#### **Phase 0: Critical UI Foundation** ✅ **COMPLETED**
- Modern sidebar navigation system
- Services matrix interface
- Calendar view improvements

#### **Phase 1: Enhanced Appointment System** ✅ **COMPLETED**
- Click-to-book calendar functionality
- Services page enhancement
- HR system integration

#### **Phase 2: Complete Admin System** ✅ **COMPLETED**
- Work patterns admin
- Employment details admin
- Holiday management system

#### **Phase 3: Commission Calculation System** ✅ **COMPLETED**
- Enhanced HR service with commission calculations
- Commission tracking in appointment costs
- Commission reports and analytics

#### **Phase 4: Advanced Calendar & Seniority System** ✅ **COMPLETED**
- 24-hour time format
- Calendar filter persistence
- Seniority-based stylist hierarchy
- Role-based color coding

### **Development Best Practices**

#### **Code Organization**
- Keep models in `app/models.py`
- Organize routes by functionality in `app/routes/`
- Place business logic in `app/services/`
- Use consistent naming conventions

#### **Testing**
- Write tests for all new functionality
- Use the comprehensive test runner for organized testing
- Maintain test coverage above 80%
- Test both happy path and edge cases

#### **Database Changes**
- Create migration scripts for schema changes
- Test migrations on development data
- Document breaking changes
- Backup production data before migrations

#### **Security**
- Always validate user input
- Use CSRF protection on forms
- Implement proper role-based access control
- Log security-relevant events

#### **Performance**
- Optimize database queries
- Use appropriate indexes
- Cache frequently accessed data
- Monitor application performance

## 🛠️ **Development Tools**

### **Docker Commands**

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f web

# Access container shell
docker exec -it salon-ese-web-1 bash

# Run tests in container
docker exec -it salon-ese-web-1 python comprehensive_test_runner.py

# Restart application
docker-compose restart web

# Rebuild container
docker-compose build --no-cache
```

### **Database Commands**

```bash
# Access database shell
docker exec -it salon-ese-db-1 psql -U salon_user -d salon_ese

# Backup database
docker exec salon-ese-db-1 pg_dump -U salon_user salon_ese > backup.sql

# Restore database
docker exec -i salon-ese-db-1 psql -U salon_user -d salon_ese < backup.sql
```

### **Python Development**

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python run.py

# Run tests
python -m pytest tests/

# Check code coverage
python -m pytest --cov=app tests/
```

## 📚 **Additional Resources**

- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Bootstrap Documentation**: https://getbootstrap.com/docs/
- **Docker Documentation**: https://docs.docker.com/

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

For more detailed contribution guidelines, see the main README.md file.
