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
- **Timezone**: pytz for UK timezone support (BST/GMT)

---

## ⚠️ Static File Serving: Development vs. Production

### Development
- The Dockerfile is configured to use Flask's built-in development server (`python run.py`).
- This allows Flask to serve static files (such as images, CSS, and JS) directly from the `static/` directory.
- You can access static files at URLs like `/static/images/your_image.png`.
- **Troubleshooting:**
    - If static files are not being served (404 errors), explicitly set the static folder and URL path in `run.py`:
    ```python
    import os
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app = create_app()
    app.static_folder = static_folder
    app.static_url_path = '/static'
    ```
    - This is necessary if `run.py` and `static/` are siblings in the project root, to ensure Flask serves static files correctly.

### Production
- In production, it is recommended to use Gunicorn (or another WSGI server) to serve the Flask app.
- **Gunicorn does not serve static files by default.**
- You must use a web server such as **Nginx** or **Apache** to serve static files from the `static/` directory.
- Example Nginx configuration:

```nginx
location /static/ {
    alias /app/static/;
}
```
- This ensures efficient serving of static assets and better performance/security.

---

### System Architecture
```
salon-ese/
├── app/                    # Main application package
│   ├── models.py          # Database models (User, Role, UserProfile, LoginAttempt)
│   ├── forms.py           # WTForms for user input validation
│   ├── utils.py           # Utility functions including timezone handling
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
├── test_timezone.py      # Timezone testing script
└── tests/                # Unit tests
```

## 👥 User Roles & Permissions

The system implements a hierarchical role-based access control system:

| Role | Level | Permissions |
|------|-------|-------------|
| **Guest** | 0 | View public pages, basic information |
| **Customer** | 1 | Book appointments, view personal profile |
| **Stylist** | 2 | Manage appointments, view customer profiles |
| **Manager** | 3 | Staff management, business reports, admin panel access |
| **Owner** | 4 | Full system access, user management, system settings |

### Role Hierarchy
- Each role inherits permissions from lower levels
- Access control is enforced at both route and template levels
- First registered user automatically becomes Owner

## 🛠️ Admin Panel

The admin panel provides comprehensive user and system management capabilities for managers and owners.

### Access Control
- **Managers**: Can access user management and role assignment
- **Owners**: Full admin access including user deletion and system settings
- **Other Roles**: No admin access

### Admin Dashboard (`/admin`)

The main admin dashboard provides an overview of system statistics and quick access to management functions.

#### Features:
- **Statistics Cards**: Real-time counts of total users, active users, customers, and stylists
- **Quick Actions**: Direct links to user management, role management, and system settings
- **Recent Users**: Table showing the 5 most recently registered users with their details
- **System Information**: Current user details, system time, database type, and timezone

#### Dashboard Statistics:
```python
# Example dashboard data
{
    'total_users': 25,
    'active_users': 23,
    'customers': 15,
    'stylists': 5,
    'recent_users': [User objects...]
}
```

### User Management (`/admin/users`)

Comprehensive user management interface with pagination and filtering.

#### Features:
- **User List**: Paginated table showing all registered users
- **User Details**: Username, full name, email, phone, roles, status, creation date
- **Status Indicators**: Visual badges for active/inactive status and email verification
- **Role Badges**: Color-coded role identification
- **Actions**: Edit and delete users (delete restricted to owners)
- **Search & Filter**: Find users quickly (future enhancement)

#### User Table Columns:
| Column | Description |
|--------|-------------|
| ID | Unique user identifier |
| Username | Login username with verification status |
| Name | First and last name |
| Email | User's email address |
| Phone | Contact number (if provided) |
| Roles | Assigned roles with color-coded badges |
| Status | Active/Inactive account status |
| Created | Registration date and time |
| Actions | Edit/Delete buttons |

#### User Actions:
- **Edit User**: Modify user details, roles, and status
- **Delete User**: Remove user account (owner only, with safety checks)
- **View Profile**: Access detailed user information

### User Editing (`/admin/users/<id>`)

Detailed user editing interface with comprehensive form validation.

#### Editable Fields:
- **Basic Information**: Username, email, first name, last name, phone
- **Account Status**: Active/inactive toggle, email verification status
- **Role Assignment**: Change user's primary role with role hierarchy display
- **System Information**: User ID, creation date, last login time

#### Role Assignment:
```python
# Available roles in hierarchy
roles = [
    ('guest', 'Guest'),
    ('customer', 'Customer'), 
    ('stylist', 'Stylist'),
    ('manager', 'Manager'),
    ('owner', 'Owner')
]
```

#### Safety Features:
- **Self-Protection**: Cannot delete your own account
- **Owner Protection**: Cannot delete the last owner account
- **Validation**: Form validation for unique usernames and emails
- **Audit Trail**: All changes are logged (future enhancement)

### Role Management (`/admin/roles`)

Comprehensive role management and assignment interface.

#### Features:
- **Role Assignment Form**: Assign roles to users with dropdown selection
- **Role Statistics**: Visual cards showing user count per role
- **Role Details Table**: Complete role information with permissions
- **Role Hierarchy Guide**: Visual guide showing role permissions and hierarchy
- **Permission Breakdown**: Detailed list of what each role can do

#### Role Statistics:
```python
# Example role statistics
{
    'owner': 1,
    'manager': 2, 
    'stylist': 5,
    'customer': 15,
    'guest': 2
}
```

#### Role Hierarchy Display:
```
Owner > Manager > Stylist > Customer > Guest
```

#### Permission Guide:
| Role | Permissions | Restrictions |
|------|-------------|--------------|
| **Owner** | Full system access, user management, role management, system settings, delete users | None |
| **Manager** | User management, role assignment, business reports, staff management | Cannot delete users |
| **Stylist** | Appointment management, customer profiles, service records | No user management |
| **Customer** | Book appointments, view personal profile | Limited access |
| **Guest** | View public pages | No authenticated features |

### System Settings (`/admin/system`)

System information and configuration interface (owner access only).

#### Features:
- **System Information**: Application version, environment, database type, timezone
- **Security Settings**: Session management, password policy, CSRF protection status
- **Database Information**: Table counts, connection status, database type
- **Maintenance Actions**: Placeholder for future maintenance features

#### System Information Display:
```python
{
    'application': 'Salon ESE',
    'version': '1.0.0',
    'environment': 'Development/Production',
    'database': 'PostgreSQL/SQLite',
    'timezone': 'UK (BST/GMT)',
    'current_time': '2025-01-27 14:30:00'
}
```

#### Database Statistics:
- User count by table
- Connection status and type
- Database URL (masked for security)

### Security Features

#### Access Control:
- **Route Protection**: All admin routes require appropriate role permissions
- **Template Protection**: Admin links only visible to authorized users
- **Form Protection**: CSRF tokens on all admin forms
- **Session Security**: Secure session management

#### Data Protection:
- **Input Validation**: All form inputs validated and sanitized
- **SQL Injection Prevention**: SQLAlchemy ORM prevents injection attacks
- **XSS Protection**: Jinja2 auto-escaping protects against XSS
- **CSRF Protection**: All forms include CSRF token validation

#### Audit Features:
- **Login Tracking**: All login attempts logged with IP and user agent
- **Action Logging**: User management actions tracked (future enhancement)
- **Error Logging**: System errors and security events logged

### UI/UX Features

#### Responsive Design:
- **Mobile-Friendly**: Admin panel works on all device sizes
- **Bootstrap Styling**: Modern, clean interface using Bootstrap 5
- **Font Awesome Icons**: Visual indicators throughout the interface

#### User Experience:
- **Flash Messages**: Success/error notifications for all actions
- **Confirmation Modals**: Safe deletion with confirmation dialogs
- **Color-Coded Badges**: Easy role and status identification
- **Loading States**: Visual feedback during operations

#### Navigation:
- **Breadcrumb Navigation**: Clear navigation hierarchy
- **Quick Actions**: Fast access to common tasks
- **Contextual Menus**: Role-appropriate action menus

### Testing Admin Functionality

#### Admin Test Script:
```bash
# Test admin functionality
docker-compose exec web python test_admin.py
```

#### Test Coverage:
- Form validation and field testing
- Role assignment functionality
- Database connectivity
- Template rendering
- Route access control

#### Manual Testing:
```bash
# Access admin panel
http://localhost:5010/admin

# Test user management
http://localhost:5010/admin/users

# Test role management  
http://localhost:5010/admin/roles

# Test system settings (owner only)
http://localhost:5010/admin/system
```

### Future Enhancements

#### Planned Features:
- **Advanced Search**: Search and filter users by various criteria
- **Bulk Operations**: Select multiple users for bulk actions
- **Audit Logging**: Detailed logs of all admin actions
- **Email Notifications**: Notify users of role changes
- **Data Export**: Export user data to CSV/Excel
- **Advanced Permissions**: Granular permission system
- **User Activity Tracking**: Monitor user login patterns
- **System Monitoring**: Real-time system health monitoring

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

## 🕐 Timezone Support

### UK Timezone Handling
The application uses UK timezone (Europe/London) for all datetime operations:
- **BST (British Summer Time)**: GMT+1 from March to October
- **GMT (Greenwich Mean Time)**: Standard time from October to March
- Automatic daylight saving time transitions
- All timestamps stored in UTC but calculated from UK time

### Timezone Functions
- `uk_now()`: Returns current time in UK timezone
- `uk_utcnow()`: Returns current UK time converted to UTC for database storage
- Used throughout the application for consistent time handling

### Testing Timezone
```bash
# Test timezone functionality
python test_timezone.py
```

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
│   ├── utils.py           # Utility functions (timezone, JSON parsing)
│   ├── routes/            # Route blueprints
│   │   ├── __init__.py
│   │   ├── auth.py        # Authentication routes
│   │   ├── main.py        # Main routes
│   │   ├── profile.py     # Profile management
│   │   └── admin.py       # Admin panel routes
│   └── templates/         # HTML templates
│       ├── base.html      # Base template
│       ├── auth/          # Authentication templates
│       ├── main/          # Main page templates
│       ├── profile/       # Profile templates
│       └── admin/         # Admin panel templates
│           ├── dashboard.html      # Admin dashboard
│           ├── users.html          # User management
│           ├── edit_user.html      # User editing
│           ├── manage_roles.html   # Role management
│           └── system_settings.html # System settings
├── config.py              # Configuration classes
├── run.py                 # Application entry point
├── requirements.txt       # Dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Service orchestration
├── .gitignore           # Git ignore rules
├── pytest.ini          # Test configuration
├── test_db.py          # Database test script
├── test_models.py      # Model test script
├── test_timezone.py    # Timezone test script
├── test_admin.py       # Admin functionality test script
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

- **v1.1.0**: Admin Panel Enhancement
  - **Admin Dashboard**: System statistics and quick actions
  - **User Management**: Comprehensive user listing and editing
  - **Role Management**: Role assignment and statistics
  - **System Settings**: System information and configuration
  - **Security Features**: Enhanced access control and data protection
  - **UI/UX Improvements**: Responsive design with Bootstrap 5
  - **Timezone Support**: UK timezone handling throughout admin panel
  - **Testing**: Admin functionality test suite

---

**Built with ❤️ for the salon management community** 