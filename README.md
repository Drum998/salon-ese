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

## 📅 Appointment Booking & Management System

The salon management system includes a comprehensive appointment booking and management feature that allows customers to book appointments with their preferred stylists and enables staff to manage schedules efficiently.

### 🆕 Recent Updates (Latest Development Session)

This section documents the comprehensive improvements made to the appointment booking and management system during the latest development session.

#### ✅ **Critical Bug Fixes**

1. **Database Transaction Bug in Appointment Booking**
   - **Issue**: `appointment_id` was referenced before the appointment was committed to the database
   - **Fix**: Added `db.session.flush()` to get the ID without committing
   - **Location**: `app/routes/appointments.py` line 75
   - **Impact**: Prevents database errors during appointment creation

2. **Missing Dashboard Templates**
   - **Issue**: `stylist_dashboard.html` and `guest_dashboard.html` were referenced but didn't exist
   - **Fix**: Created both templates with proper functionality
   - **Files Created**: 
     - `app/templates/main/stylist_dashboard.html`
     - `app/templates/main/guest_dashboard.html`
   - **Impact**: Eliminates 404 errors when accessing dashboards

3. **Missing Role Assignment Logic**
   - **Issue**: New users weren't assigned a default role during registration
   - **Fix**: Added automatic assignment of 'customer' role to new users
   - **Location**: `app/routes/auth.py`
   - **Impact**: Ensures all users have appropriate permissions

#### 🔧 **Navigation and Routing Fixes**

1. **Broken Booking Buttons**
   - **Fixed**: Main index page "Book Appointment" button now correctly points to booking page for customers
   - **Fixed**: Services page "Book Appointment" button now correctly points to booking page for customers  
   - **Fixed**: Customer dashboard "Book Now" and "Book Appointment" buttons now have proper URLs
   - **Fixed**: Customer dashboard "View History" button now points to appointments page
   - **Files Modified**: 
     - `app/templates/main/index.html`
     - `app/templates/main/services.html`
     - `app/templates/main/customer_dashboard.html`

2. **Stylist Dashboard "View Schedule" Error**
   - **Issue**: Template was trying to compare time objects incorrectly using Jinja2 filters
   - **Fix**: Created helper function `get_appointments_for_slot()` for proper time comparison
   - **Files Modified**: `app/routes/appointments.py`, `app/templates/appointments/stylist_calendar.html`
   - **Impact**: Stylists can now view their calendar without errors

#### 🎨 **User Interface Improvements**

1. **Customer Dashboard Enhancement**
   - **Added**: Dynamic display of upcoming appointments in a table format
   - **Added**: Appointment details including date, time, service, stylist, and status
   - **Added**: Action buttons to view appointment details
   - **Added**: Proper handling of empty appointment states
   - **File Modified**: `app/templates/main/customer_dashboard.html`

2. **Stylist Calendar Week View**
   - **Fixed**: Time slot filtering to properly display appointments in calendar grid
   - **Enhanced**: Visual styling for appointment slots with customer information
   - **Added**: Status badges and proper time formatting
   - **File Modified**: `app/templates/appointments/stylist_calendar.html`

#### 🚀 **New Features Added**

1. **Appointment Cancellation System**
   - **Added**: Cancel appointment functionality with proper permissions
   - **Added**: Status history tracking for cancellations
   - **Added**: Cancel button in appointment view template
   - **Files Modified**: 
     - `app/routes/appointments.py` (new route)
     - `app/templates/appointments/view_appointment.html`

2. **Enhanced Error Handling**
   - **Added**: Warning messages in booking form when no stylists or services are available
   - **Added**: Better user feedback for missing data
   - **File Modified**: `app/templates/appointments/book.html`

3. **Service Initialization Script**
   - **Created**: `init_services.py` script to populate sample services
   - **Features**: Sample hair services with realistic pricing and durations
   - **Usage**: Run `python init_services.py` to initialize services

#### 📊 **Logging and Debugging**

1. **Comprehensive Logging System**
   - **Added**: Customer dashboard access logging
   - **Added**: Stylist calendar view logging
   - **Added**: Appointment booking logging
   - **Added**: Debug information sent to Docker logs instead of UI
   - **Files Modified**: 
     - `app/routes/main.py`
     - `app/routes/appointments.py`

2. **Debug Information**
   - **Removed**: Debug alerts from customer dashboard
   - **Removed**: Debug cards from stylist calendar
   - **Added**: Structured logging to Docker container logs
   - **Benefit**: Clean UI while maintaining debugging capability

#### 🔍 **Template Context Fixes**

1. **Missing Template Variables**
   - **Fixed**: Added `timedelta`, `calendar`, and `date` objects to template context
   - **Fixed**: Added `get_appointments_for_slot` helper function
   - **Files Modified**: `app/routes/appointments.py`
   - **Impact**: Eliminates template rendering errors

#### 📋 **Files Created/Modified Summary**

**New Files:**
- `app/templates/main/stylist_dashboard.html` - Stylist dashboard template
- `app/templates/main/guest_dashboard.html` - Guest dashboard template
- `init_services.py` - Service initialization script
- `create_favicon.py` - Script to generate PNG favicon from SVG logo

**Modified Files:**
- `app/routes/appointments.py` - Fixed booking bug, added cancellation, enhanced logging
- `app/routes/main.py` - Fixed dashboard routing, added logging
- `app/routes/auth.py` - Added default role assignment
- `app/templates/main/customer_dashboard.html` - Enhanced appointment display
- `app/templates/main/index.html` - Fixed booking button routing
- `app/templates/main/services.html` - Fixed booking button routing
- `app/templates/appointments/book.html` - Enhanced error handling
- `app/templates/appointments/stylist_calendar.html` - Fixed time filtering
- `app/templates/appointments/view_appointment.html` - Added cancel button
- `app/templates/base.html` - Updated logo to use logo_4.svg and added favicon support

#### 🧪 **Testing Recommendations**

1. **Customer Flow Testing**
   ```bash
   # Test customer registration and booking
   1. Register as a new customer
   2. Verify default 'customer' role assignment
   3. Book an appointment
   4. Check customer dashboard shows upcoming appointments
   5. View appointment history
   ```

2. **Stylist Flow Testing**
   ```bash
   # Test stylist calendar functionality
   1. Create a stylist user via admin panel
   2. Log in as stylist
   3. Access stylist dashboard
   4. Click "View Schedule" to access calendar
   5. Verify week view displays appointments correctly
   ```

3. **Admin Flow Testing**
   ```bash
   # Test appointment management
   1. Log in as manager/owner
   2. Access admin appointments view
   3. Test appointment status updates
   4. Verify appointment cancellation works
   ```

#### 🐛 **Known Issues Resolved**

1. **Appointment Booking Errors**: Fixed database transaction issues
2. **Missing Dashboard Pages**: Created all required dashboard templates
3. **Broken Navigation**: Fixed all booking button routing
4. **Calendar Display Issues**: Fixed time comparison in week view
5. **Role Assignment**: Ensured new users get appropriate roles

#### 📈 **Performance Improvements**

1. **Database Queries**: Optimized appointment queries with proper filtering
2. **Template Rendering**: Fixed context variable issues
3. **User Experience**: Streamlined navigation and reduced error states
4. **Logging**: Moved debug info to logs for better performance

#### 🎨 **Branding and UI Updates**

1. **Logo Update**
   - **Changed**: Updated logo from `logo_2.png` to `logo_4.svg`
   - **Benefits**: SVG format provides better quality at all sizes and smaller file size
   - **Location**: Navigation bar in all pages via base template

2. **Favicon Implementation**
   - **Added**: SVG favicon using `logo_4.svg` for modern browsers
   - **Added**: PNG fallback favicon for older browsers
   - **Created**: `create_favicon.py` script to generate PNG favicon from SVG
   - **Benefits**: Professional branding in browser tabs and bookmarks

This comprehensive update significantly improves the reliability, user experience, and functionality of the appointment booking and management system.

### Features

#### For Customers
- **Book Appointments**: Choose from available stylists and services
- **View Appointments**: See upcoming and past appointments
- **Contact Information**: Provide phone/email for notifications
- **Service Selection**: Browse available services with pricing
- **Time Slot Selection**: Choose from available 30-minute time slots (9 AM - 6 PM)

#### For Stylists
- **Calendar View**: Week and month calendar views of appointments
- **Schedule Management**: View upcoming appointments and today's schedule
- **Appointment Details**: Access customer information and service details
- **Status Updates**: Mark appointments as completed, cancelled, or no-show

#### For Managers/Owners
- **All Appointments View**: See appointments across all stylists
- **Filtering Options**: Filter by stylist, status, and date range
- **Statistics Dashboard**: View appointment statistics and trends
- **Service Management**: Add, edit, and manage salon services
- **Status Management**: Update appointment statuses with notes

### Database Models

#### Service
- `name`: Service name (e.g., "Haircut & Style")
- `description`: Detailed service description
- `duration`: Duration in minutes
- `price`: Service price in GBP
- `is_active`: Whether the service is available for booking

#### Appointment
- `customer_id`: Reference to the customer
- `stylist_id`: Reference to the stylist
- `service_id`: Reference to the service
- `appointment_date`: Date of the appointment
- `start_time` / `end_time`: Appointment time slot
- `customer_phone` / `customer_email`: Contact information for notifications
- `notes`: Additional notes about the appointment
- `status`: Appointment status (confirmed, completed, cancelled, no-show)

#### AppointmentStatus
- Tracks the history of status changes
- Records who made the change and when
- Includes notes for each status change

### User Roles & Permissions

| Role | Appointment Permissions |
|------|------------------------|
| **Customer** | Book appointments, view own appointments, modify upcoming appointments |
| **Stylist** | View own schedule, update appointment status, view customer details |
| **Manager** | View all appointments, manage services, update any appointment status |
| **Owner** | Full access to all appointment features |

### Setup Instructions

1. **Database Migration**: The appointment tables are created automatically when the app starts
2. **Initialize Services**: Run the service initialization script:
   ```bash
   python init_services.py
   ```
3. **Create Stylist Users**: Use the admin panel to create users with the 'stylist' role
4. **Create Customer Users**: Users can register as customers or be created via admin panel

### API Endpoints

#### Customer Endpoints
- `GET/POST /appointments/book` - Book a new appointment
- `GET /appointments/my-appointments` - View customer's appointments

#### Stylist Endpoints
- `GET /appointments/stylist-appointments` - View stylist's calendar
- `GET /appointments/appointment/<id>` - View appointment details
- `GET/POST /appointments/appointment/<id>/edit` - Edit appointment

#### Admin Endpoints
- `GET /appointments/admin-appointments` - View all appointments
- `GET /appointments/services` - Manage services
- `GET/POST /appointments/services/new` - Add new service
- `GET/POST /appointments/services/<id>/edit` - Edit service

#### API Endpoints
- `GET /appointments/api/appointments` - JSON API for calendar data

### Calendar Views

#### Week View
- Shows appointments in a weekly grid format
- Time slots from 9 AM to 6 PM in 30-minute intervals
- Color-coded appointment status
- Click to view appointment details

#### Month View
- Monthly calendar overview
- Shows appointment counts per day
- Quick navigation between months
- Filtering by stylist and status

### Conflict Prevention

The system automatically prevents double-booking by:
- Checking for time conflicts when booking appointments
- Validating stylist availability
- Ensuring appointments don't overlap
- Providing clear error messages for conflicts

### Status Management

Appointments can have the following statuses:
- **Confirmed**: Appointment is scheduled and confirmed
- **Completed**: Service has been provided
- **Cancelled**: Appointment was cancelled
- **No Show**: Customer didn't attend

Each status change is tracked with:
- Timestamp of the change
- User who made the change
- Optional notes explaining the change

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