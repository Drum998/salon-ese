# Salon ESE - API Documentation

This document provides comprehensive documentation for the Salon ESE authentication and user management system API endpoints.

## 🔗 Base URL
- **Development**: `http://localhost:5010`
- **Production**: `https://your-domain.com`

## 🔐 Authentication Endpoints

### User Registration
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

**Notes:**
- First registered user automatically becomes Owner
- Email verification is required (except for first user)
- Password must meet security requirements

### User Login
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

**Security Features:**
- Login attempts are logged with IP and user agent
- Failed attempts are tracked for security monitoring
- Session timeout based on configuration

### User Logout
**GET** `/auth/logout`

Terminate user session.

**Response:**
- **Success (302)**: Redirects to home page
- **Requires**: Authentication

## 👤 Profile Management Endpoints

### View Profile
**GET** `/profile`

Display user's profile information.

**Response:**
- **Success (200)**: Profile page with user data
- **Requires**: Authentication

### Edit Profile
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

**Stylist-Specific Fields:**
```json
{
  "specialties": ["haircuts", "coloring", "styling"],
  "experience_years": 5,
  "certifications": ["cosmetology_license", "advanced_coloring"],
  "availability": {
    "monday": ["09:00-17:00"],
    "tuesday": ["09:00-17:00"],
    "wednesday": ["09:00-17:00"],
    "thursday": ["09:00-17:00"],
    "friday": ["09:00-17:00"]
  }
}
```

**Customer-Specific Fields:**
```json
{
  "preferred_stylist_id": 123,
  "hair_type": "curly",
  "allergies": ["certain_dyes", "specific_products"],
  "notes": "Prefers organic products"
}
```

### Change Password
**GET/POST** `/profile/change-password`

Update user password.

**Request Body (POST):**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newsecurepassword456",
  "confirm_password": "newsecurepassword456"
}
```

## 🏠 Main Application Endpoints

### Home Page
**GET** `/`

Public home page with salon information.

**Response:**
- **Success (200)**: Home page with public content
- **Access**: Public (no authentication required)

### Services Page
**GET** `/services`

Display salon services and pricing.

**Response:**
- **Success (200)**: Services page
- **Access**: Public

### About Page
**GET** `/about`

Salon information and team details.

**Response:**
- **Success (200)**: About page
- **Access**: Public

### Contact Page
**GET** `/contact`

Contact information and form.

**Response:**
- **Success (200)**: Contact page
- **Access**: Public

## 👨‍💼 Admin Panel Endpoints

### Admin Dashboard
**GET** `/admin`

Admin dashboard with system overview.

**Response:**
- **Success (200)**: Admin dashboard
- **Requires**: Owner role

### User Management
**GET** `/admin/users`

List all users in the system.

**Query Parameters:**
- `page`: Page number for pagination
- `per_page`: Items per page (default: 20)
- `search`: Search term for username/email
- `role`: Filter by role

**Response:**
- **Success (200)**: User list page
- **Requires**: Owner role

### Edit User
**GET/POST** `/admin/users/<int:user_id>`

Edit user information and roles.

**Request Body (POST):**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "email_verified": true,
  "roles": ["customer", "stylist"]
}
```

**Response:**
- **Success (200/302)**: User edit page or redirect
- **Requires**: Owner role

### Role Management
**GET** `/admin/roles`

Manage system roles and permissions.

**Response:**
- **Success (200)**: Role management page
- **Requires**: Owner role

## 🔒 Role-Based Access Control

### Role Hierarchy
```
Owner (4) > Manager (3) > Stylist (2) > Customer (1) > Guest (0)
```

### Access Control Matrix

| Endpoint | Guest | Customer | Stylist | Manager | Owner |
|----------|-------|----------|---------|---------|-------|
| `/` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/auth/login` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/auth/register` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/profile` | ❌ | ✅ | ✅ | ✅ | ✅ |
| `/admin` | ❌ | ❌ | ❌ | ❌ | ✅ |
| `/admin/users` | ❌ | ❌ | ❌ | ❌ | ✅ |

### Permission Checking
```python
# In templates
{% if current_user.can_access('manager') %}
  <!-- Manager-only content -->
{% endif %}

# In routes
@login_required
def admin_panel():
    if not current_user.can_access('owner'):
        abort(403)
    # Admin functionality
```

## 📊 Database Models

### User Model
```python
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "is_active": true,
  "email_verified": true,
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-15T10:30:00Z"
}
```

### Role Model
```python
{
  "id": 1,
  "name": "stylist",
  "description": "Hair stylist with appointment management",
  "permissions": "['manage_appointments', 'view_customers']",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### UserProfile Model
```python
{
  "id": 1,
  "user_id": 1,
  "bio": "Professional hair stylist",
  "profile_image": "uploads/profile_1.jpg",
  "date_of_birth": "1990-01-01",
  "address": "123 Main St",
  "emergency_contact": "Jane Doe",
  "emergency_phone": "+1234567890",
  "specialties": "['haircuts', 'coloring']",
  "experience_years": 5,
  "certifications": "['cosmetology_license']",
  "availability": "{'monday': ['09:00-17:00']}",
  "preferred_stylist_id": null,
  "hair_type": null,
  "allergies": null,
  "notes": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## 🛡️ Security Features

### CSRF Protection
All POST requests require CSRF tokens:
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

### Session Security
- Secure session configuration
- Configurable session timeout
- Session invalidation on logout

### Input Validation
- WTForms validation on all inputs
- SQL injection prevention via SQLAlchemy ORM
- XSS protection via Jinja2 auto-escaping

### Security Monitoring
```python
# Login attempt tracking
{
  "id": 1,
  "user_id": 1,
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "success": true,
  "attempted_at": "2024-01-15T10:30:00Z"
}
```

## 🧪 Testing Endpoints

### Health Check
**GET** `/health`

Check application health status.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Test Database Connection
**GET** `/test/db`

Test database connectivity (development only).

## 📝 Error Handling

### Standard Error Responses

**400 Bad Request**
```json
{
  "error": "Validation failed",
  "details": {
    "username": ["Username is required"],
    "email": ["Invalid email format"]
  }
}
```

**401 Unauthorized**
```json
{
  "error": "Authentication required",
  "message": "Please log in to access this resource"
}
```

**403 Forbidden**
```json
{
  "error": "Access denied",
  "message": "You don't have permission to access this resource"
}
```

**404 Not Found**
```json
{
  "error": "Resource not found",
  "message": "The requested resource was not found"
}
```

**500 Internal Server Error**
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db

# Optional
FLASK_DEBUG=1
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-password
```

### Session Configuration
```python
PERMANENT_SESSION_LIFETIME = timedelta(days=7)
SESSION_COOKIE_SECURE = True  # Production only
SESSION_COOKIE_HTTPONLY = True
```

## 📚 Usage Examples

### Python Client Example
```python
import requests

# Login
session = requests.Session()
login_data = {
    'username': 'johndoe',
    'password': 'securepassword123'
}
response = session.post('http://localhost:5010/auth/login', data=login_data)

# Access protected endpoint
profile_response = session.get('http://localhost:5010/profile')
```

### JavaScript Client Example
```javascript
// Login
const loginData = {
    username: 'johndoe',
    password: 'securepassword123'
};

fetch('/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(loginData)
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🔄 Rate Limiting

Currently, the API does not implement rate limiting. For production deployment, consider implementing:

- Request rate limiting per IP
- Login attempt throttling
- API endpoint rate limiting

## 📈 Monitoring

### Logging
- Application logs: `logs/app.log`
- Access logs: `logs/access.log`
- Error logs: `logs/error.log`

### Metrics
- User registration rate
- Login success/failure rates
- API endpoint usage
- Database connection health

---

**For additional support, please refer to the main README.md file or create an issue on GitHub.** 