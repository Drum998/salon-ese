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
- **UI**: Modern sidebar navigation with responsive design

---

## 🆕 Latest Release: v2.2.0 - Complete Admin System

### 🎯 Overview
The latest release completes the core admin system with fully functional Work Patterns and Employment Details management. This major update provides comprehensive staff management capabilities with proper form validation, HR integration, and salon hours integration.

### ✨ New Features in v2.2.0

#### 1. **Work Patterns Admin System** ✅ **COMPLETED**
- **Purpose**: Complete management of stylist work schedules and patterns
- **Implementation**: Full CRUD operations with salon hours integration
- **Features**:
  - Complete work pattern creation, editing, and deletion
  - Weekly schedule management with time validation
  - Integration with appointment booking system
  - Holiday entitlement calculations based on weekly hours
  - Salon hours integration for availability validation
  - Comprehensive form validation and error handling

#### 2. **Employment Details Admin System** ✅ **COMPLETED**
- **Purpose**: Complete management of staff employment information
- **Implementation**: Enhanced admin interface with HR system integration
- **Features**:
  - Complete CRUD operations for employment details
  - Employment type-specific validation (employed vs self-employed)
  - Integration with appointment cost calculations
  - Enhanced form validation with proper error handling
  - HR system integration for financial tracking
  - Safe numeric field conversion and validation

#### 3. **Enhanced Form Validation** ✅ **COMPLETED**
- **Purpose**: Robust form handling and error prevention
- **Implementation**: Fixed form validation issues and improved user experience
- **Features**:
  - Fixed user_id field validation
  - Safe float conversion for numeric fields
  - Employment type-specific field validation
  - Proper error messages and user feedback
  - Form state preservation on validation errors

### 🔧 Technical Implementation

#### Work Patterns Integration
```python
# WorkPattern model with salon hours integration
class WorkPattern(db.Model):
    work_schedule = db.Column(db.JSON, nullable=False)  # Weekly schedule
    is_active = db.Column(db.Boolean, default=True)
    
    def get_weekly_hours(self):
        # Calculate total weekly hours from schedule
```

#### Employment Details Integration
```python
# Enhanced EmploymentDetails with HR fields
class EmploymentDetails(db.Model):
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    hourly_rate = db.Column(db.Numeric(8, 2), nullable=True)
    commission_rate = db.Column(db.Numeric(5, 2), nullable=True)
    base_salary = db.Column(db.Numeric(10, 2), nullable=True)
```

#### Form Validation Fixes
```python
# Fixed user_id field validation
user_id = SelectField('Staff Member', validators=[DataRequired()])

def validate_user_id(self, field):
    if not field.data or field.data == '':
        raise ValidationError('Please select a staff member.')
    try:
        user_id = int(field.data)
        # Additional validation...
    except ValueError:
        raise ValidationError('Please select a valid staff member.')
```

### 🎨 User Interface Enhancements

#### Work Patterns Admin
- **Complete CRUD Interface**: Create, read, update, delete work patterns
- **Weekly Schedule Management**: Visual interface for setting work hours
- **Time Validation**: Proper time format validation and error handling
- **Integration Display**: Shows integration with salon hours and appointments

#### Employment Details Admin
- **Enhanced Forms**: Employment type-specific field visibility
- **Validation Feedback**: Clear error messages and form state preservation
- **HR Integration**: Shows connection with cost calculations and financial tracking
- **Responsive Design**: Works on all device sizes

### 📊 Business Benefits

#### For Salon Owners/Managers
- **Complete Staff Management**: Full control over work patterns and employment details
- **Accurate Scheduling**: Work patterns integrated with appointment booking
- **Financial Tracking**: Employment details linked to cost calculations
- **Holiday Management**: Automatic entitlement calculations based on work patterns

#### For Stylists
- **Clear Work Schedules**: Visual representation of work patterns
- **Employment Transparency**: Clear view of employment terms and rates
- **Holiday Tracking**: Automatic calculation of holiday entitlements

### 🚀 Migration Instructions

For users updating from previous versions:

1. **Stop the current container:**
   ```bash
   docker-compose down
   ```

2. **Rebuild with latest code:**
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Test the new admin features:**
   - Access Work Patterns: Admin > Work Patterns
   - Access Employment Details: Admin > Employment Details
   - Test form validation and error handling
   - Verify integration with existing systems

### 🧪 Testing the New Features

#### Work Patterns Testing
```bash
# 1. Test work pattern creation
- Navigate to Admin > Work Patterns
- Create a new work pattern for a stylist
- Set weekly schedule with proper time formats
- Verify pattern is saved and displayed correctly

# 2. Test appointment integration
- Book an appointment for the stylist
- Verify time slots respect work pattern
- Test outside work hours (should be blocked)

# 3. Test holiday calculations
- Check holiday entitlement calculations
- Verify based on weekly hours from work pattern
```

#### Employment Details Testing
```bash
# 1. Test employment details creation
- Navigate to Admin > Employment Details
- Create employment details for a stylist
- Test both employed and self-employed types
- Verify form validation and error handling

# 2. Test HR integration
- Book an appointment for the stylist
- Check appointment cost calculations
- Verify employment details affect cost calculations

# 3. Test form validation
- Try submitting forms with invalid data
- Verify proper error messages
- Test empty field handling
```

#### Verification Checklist
- [ ] Work patterns can be created, edited, and deleted
- [ ] Employment details forms work without validation errors
- [ ] Work patterns integrate with appointment booking
- [ ] Employment details integrate with cost calculations
- [ ] Form validation provides clear error messages
- [ ] All existing functionality still works
- [ ] Admin interface is responsive and user-friendly

---

## 🆕 Previous Release: v2.0.0 - HR System Integration

### 🎯 Overview
The latest release introduces comprehensive HR System Integration with financial tracking, cost calculations, and employment management. This major update provides salon owners and managers with detailed insights into appointment profitability, stylist earnings, and employment costs.

### ✨ New Features in v2.0.0

#### 1. **HR System Integration**
- **Purpose**: Track employment details, calculate appointment costs, and manage financial performance
- **Implementation**: Extended employment details with HR fields and new appointment cost tracking
- **Features**:
  - Employment start/end dates and pay rates
  - Hourly rate and commission rate tracking
  - Base salary management for employed staff
  - Automatic appointment cost calculations
  - Financial reporting and profit analysis

#### 2. **Enhanced Employment Details**
- **New Fields**: `start_date`, `end_date`, `hourly_rate`, `commission_rate`, `base_salary`
- **Employment Types**: Support for both employed and self-employed stylists
- **Date Management**: Track employment periods with start and end dates
- **Rate Calculations**: Automatic cost calculations based on employment type
- **Validation**: Comprehensive form validation for employment-specific fields

#### 3. **Appointment Cost Tracking**
- **New Model**: `AppointmentCost` for detailed cost breakdowns
- **Cost Components**: Service revenue, stylist cost, salon profit
- **Calculation Methods**: Hourly rate and commission-based calculations
- **Automatic Integration**: Costs calculated automatically when appointments are booked
- **Financial Transparency**: Clear breakdown of revenue, costs, and profit per appointment

#### 4. **HR Dashboard & Reports**
- **HR Dashboard**: Comprehensive financial overview with filtering options
- **Financial Summary**: Total revenue, salon profit, stylist costs, profit margin
- **Employment Summary**: Stylist counts, employment types, monthly base costs
- **Appointment Costs**: Detailed cost breakdowns with filtering and pagination
- **Stylist Earnings**: Earnings reports with date range filtering and rankings

#### 5. **Business Logic Layer**
- **HRService Class**: Dedicated service layer for HR calculations
- **Cost Calculations**: Automatic appointment cost calculations
- **Earnings Reports**: Stylist earnings aggregation over time periods
- **Profit Analysis**: Salon profit calculations with date filtering
- **Performance Reports**: Detailed stylist performance analysis

### 🔧 Technical Implementation

#### Database Schema Changes
```sql
-- Enhanced EmploymentDetails table
ALTER TABLE employment_details ADD COLUMN start_date DATE NOT NULL DEFAULT CURRENT_DATE;
ALTER TABLE employment_details ADD COLUMN end_date DATE;
ALTER TABLE employment_details ADD COLUMN hourly_rate NUMERIC(8,2);
ALTER TABLE employment_details ADD COLUMN commission_rate NUMERIC(5,2);
ALTER TABLE employment_details ADD COLUMN base_salary NUMERIC(10,2);

-- New AppointmentCost table
CREATE TABLE appointment_cost (
    id SERIAL PRIMARY KEY,
    appointment_id INTEGER REFERENCES appointment(id),
    stylist_id INTEGER REFERENCES user(id),
    service_revenue NUMERIC(10,2) NOT NULL,
    stylist_cost NUMERIC(10,2) NOT NULL,
    salon_profit NUMERIC(10,2) NOT NULL,
    calculation_method VARCHAR(20) NOT NULL,
    hours_worked NUMERIC(4,2),
    commission_amount NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### New Models
- **Enhanced EmploymentDetails**: Added HR fields and calculation methods
- **AppointmentCost**: Tracks cost breakdowns for each appointment
- **HRService**: Business logic layer for HR calculations

#### New Routes
- `/admin/hr-dashboard` - HR dashboard with financial overview
- `/admin/hr/appointment-costs` - Detailed appointment cost breakdowns
- `/admin/hr/stylist-earnings` - Stylist earnings reports
- Enhanced employment details routes with new fields

#### New Templates
- `admin/hr_dashboard.html` - HR dashboard with financial summary
- `admin/appointment_costs.html` - Appointment cost breakdowns
- `admin/stylist_earnings.html` - Stylist earnings reports
- Enhanced `admin/employment_details_form.html` - New HR fields

### 🎨 User Interface Enhancements

#### HR Dashboard Features
- **Financial Summary Cards**: Total Revenue, Salon Profit, Stylist Costs, Profit Margin
- **Employment Summary**: Total Stylists, Employed/Self-employed counts, Monthly Base Cost
- **Filtering Options**: Date range, stylist, and employment type filters
- **Performance Reports**: Stylist performance when filtered by specific stylist
- **Responsive Design**: Works on all screen sizes

#### Appointment Cost Management
- **Detailed Breakdowns**: Service revenue, stylist cost, salon profit, profit margin
- **Calculation Methods**: Hourly rate vs commission-based calculations
- **Filtering & Pagination**: Date range and stylist filtering with pagination
- **Visual Indicators**: Color-coded profit margins and calculation methods

#### Enhanced Employment Forms
- **Dynamic Fields**: Employment-type-specific fields (hourly rate vs commission rate)
- **Date Management**: Start and end date fields with validation
- **Rate Validation**: Proper validation for different employment types
- **Client-side Logic**: JavaScript for dynamic field visibility

### 📊 Business Benefits

#### For Salon Owners/Managers
- **Financial Transparency**: Clear view of appointment profitability
- **Cost Control**: Track stylist costs and profit margins
- **Employment Management**: Comprehensive employment details tracking
- **Performance Analysis**: Stylist earnings and performance reports
- **Data-Driven Decisions**: Financial insights for business planning

#### For Stylists
- **Earnings Tracking**: Clear view of earnings and performance
- **Employment Clarity**: Transparent employment terms and rates
- **Performance Insights**: Understanding of cost vs revenue

#### For Business Operations
- **Automated Calculations**: No manual cost calculations required
- **Accurate Reporting**: Reliable financial data for decision making
- **Compliance**: Proper employment record keeping
- **Scalability**: System grows with business needs

### 🚀 Migration Instructions

For users updating from previous versions:

1. **Stop the current container:**
   ```bash
   docker-compose down
   ```

2. **Run HR system migration:**
   ```bash
   docker exec -it salon-ese-web-1 python migrate_hr_system.py
   ```

3. **Test the new features:**
   - Access HR Dashboard from admin panel
   - Create employment details with new HR fields
   - Book appointments to see automatic cost calculations
   - View appointment cost breakdowns and stylist earnings

### 🧪 Testing the New Features

#### HR System Testing
```bash
# 1. Test employment details with HR fields
- Navigate to Employment Details management
- Create employment details with start dates and rates
- Verify form validation for different employment types
- Test date range validation

# 2. Test appointment cost calculations
- Book appointments with stylists who have employment details
- Verify automatic cost calculations
- Check appointment cost breakdowns in admin panel
- Verify profit margin calculations

# 3. Test HR dashboard
- Access HR Dashboard from admin panel
- Verify financial summary cards display correctly
- Test filtering by date range and stylist
- Check employment summary statistics

# 4. Test reports
- View appointment costs with filtering
- Check stylist earnings reports
- Verify date range filtering works
- Test pagination in reports
```

#### Verification Checklist
- [ ] HR Dashboard displays financial summary correctly
- [ ] Employment details form includes new HR fields
- [ ] Appointment costs are calculated automatically
- [ ] Cost breakdowns show in appointment view
- [ ] Stylist earnings reports work with filtering
- [ ] All employment types (employed/self-employed) work correctly
- [ ] Date validation works for employment periods
- [ ] Financial calculations are accurate

---

## 🆕 Previous Release: v1.9.0 - Services Page Layout Improvements

### 🎯 Overview
The latest release focuses on improving the Services page layout and user experience. Services are now prominently displayed above the assignment matrix, and stylist rows have been made more compact for better space efficiency and visual clarity.

### ✨ New Features in v1.9.0

#### 1. **Services Page Layout Enhancement**
- **Purpose**: Improve information hierarchy and space efficiency
- **Implementation**: Services cards moved above matrix, compact stylist rows
- **Features**:
  - Service cards prominently displayed at top of page
  - Compact stylist matrix rows (username only)
  - Reduced column widths and padding for better space usage
  - Simplified service headers in matrix
  - Maintained all existing functionality
  - Better responsive design for smaller screens

#### 2. **Improved Information Hierarchy**
- **Service Cards**: Detailed service information displayed first
- **Matrix**: Assignment matrix moved below for secondary focus
- **Visual Flow**: Natural top-to-bottom information flow
- **User Experience**: Easier to review services before managing assignments

#### 3. **Compact Matrix Design**
- **Stylist Display**: Username only (removed full names and roles)
- **Space Efficiency**: Much more compact rows for better space utilization
- **Visual Clarity**: Cleaner matrix with less visual clutter
- **Data Preservation**: Full names still available in data attributes

#### 4. **Enhanced Responsive Design**
- **Column Widths**: Reduced from 150px to 120px
- **Padding**: Compact padding (0.25rem) for tighter layout
- **Font Sizes**: Smaller fonts (0.85rem) for more efficient display
- **Mobile Friendly**: Better behavior on smaller screens

### ✨ Previous Major Features

#### **v1.8.0 - Click-to-Book Calendar with Single Block Spanning**
- **Purpose**: Direct calendar interaction for booking appointments
- **Features**:
  - 5-minute time slot granularity
  - Click-to-book functionality on calendar time slots
  - Pre-filled booking form with selected parameters
  - Day navigation buttons for easy week navigation
  - Sticky stylist header for better usability
  - Single appointment block spanning (CSS method)
  - Narrower time slot display (10px height)
  - Appointment duration blocking (prevents double-booking)

#### **v1.4.0 - Modern Sidebar Navigation System**
- **Purpose**: Improve navigation organization and scalability
- **Features**:
  - Fixed sidebar with collapsible functionality
  - Role-based menu organization
  - Responsive design for mobile devices
  - Smooth animations and transitions

#### 1. **Modern Sidebar Navigation**
- **Purpose**: Improve navigation organization and scalability for future features
- **Implementation**: Fixed sidebar with collapsible functionality
- **Features**:
  - Fixed sidebar on the left side of the screen
  - Collapsible sidebar for more content space
  - Role-based menu organization
  - Responsive design for mobile devices
  - Smooth animations and transitions
  - Active page highlighting

#### 2. **Enhanced User Experience**
- **Top Bar**: User information and sidebar toggle button
- **Page Titles**: Dynamic page titles in the top bar
- **Flash Messages**: Fixed position notifications with auto-hide
- **Mobile Overlay**: Touch-friendly mobile navigation
- **Visual Feedback**: Hover effects and active states

#### 3. **Responsive Design**
- **Desktop**: Full sidebar with collapse/expand functionality
- **Tablet**: Adaptive sidebar with touch support
- **Mobile**: Overlay sidebar with backdrop
- **Breakpoints**: Optimized for all screen sizes

#### 4. **Services Matrix Interface** ✅ **COMPLETED**
- **Purpose**: Streamline stylist-service assignment management
- **Implementation**: Matrix layout with checkboxes for easy assignment
- **Features**:
  - Stylists in first column, services along top
  - Checkbox interface for quick assignments
  - Bulk save functionality
  - Change tracking and visual feedback
  - Service details displayed in headers
  - Responsive design for all screen sizes

#### 5. **Calendar View Improvements** ✅ **COMPLETED**
- **Purpose**: Better organization for viewing all appointments with stylist names along the top
- **Implementation**: Redesigned week view with stylists as columns
- **Features**:
  - Stylist names as column headers
  - Days as row headers with time slots
  - Appointment counts per stylist per day
  - Color-coded appointment status
  - Enhanced visual organization
  - Maintains existing month view and filters

### 🔧 Technical Implementation

#### CSS Variables for Theming
```css
:root {
    --sidebar-width: 280px;
    --sidebar-collapsed-width: 70px;
    --primary-color: #d63384;
    --secondary-color: #9b7bb7;
    --sidebar-bg: #2c3e50;
    --sidebar-hover: #34495e;
    --sidebar-text: #ecf0f1;
    --sidebar-active: #3498db;
}
```

#### JavaScript Functionality
```javascript
// Sidebar toggle functionality
sidebarToggle.addEventListener('click', function() {
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
});

// Services matrix bulk save
function saveAllAssociations() {
    // Collect checkbox states and send to server
    const associations = [];
    checkboxes.forEach(checkbox => {
        associations.push({
            stylist_id: parseInt(checkbox.dataset.stylistId),
            service_id: parseInt(checkbox.dataset.serviceId),
            is_allowed: checkbox.checked
        });
    });
    // Send to bulk update endpoint
}

// Calendar view improvements
// - Stylists as column headers for better organization
// - Day-based layout with time slots
// - Appointment counts and status indicators
// - Responsive design for all screen sizes
```

### 🎨 Navigation Structure

#### Main Section
- **Home**: Landing page
- **Services**: Public services page
- **Dashboard**: User dashboard (authenticated users)

#### Appointments Section
- **Book Appointment**: Appointment booking
- **My Appointments**: Customer appointments
- **My Schedule**: Stylist schedule
- **All Appointments**: Admin view

#### Management Section (Managers/Owners)
- **Services**: Service management with matrix interface
- **Stylist Timings**: Custom timing management
- **Stylist Associations**: Service permissions
- **Admin Panel**: Full admin access

#### Account Section
- **My Profile**: User profile management
- **Login/Register**: Authentication (guests)
- **Logout**: Session termination

#### Information Section
- **About**: Salon information
- **Contact**: Contact details

### 🛣️ Enhanced Templates

#### Base Template Updates
- **New Sidebar Structure**: Organized navigation sections
- **Top Bar**: User info and navigation controls
- **Content Wrapper**: Proper spacing and layout
- **Flash Messages**: Fixed position notifications

#### Services Matrix Template
- **Matrix Table**: Stylists vs services with checkboxes
- **Service Headers**: Duration, price, and waiting time info
- **Stylist Info**: Names, usernames, and role badges
- **Bulk Save**: Single button to save all assignments
- **Change Tracking**: Visual feedback for unsaved changes

#### Page Title Integration
- **Dynamic Titles**: Page titles in top bar
- **Consistent Branding**: Logo and branding in sidebar
- **User Context**: Current user and role display

### 📁 Files Modified

#### Core Template
- `app/templates/base.html` - Complete navigation redesign

#### Services Management
- `app/templates/appointments/services.html` - Matrix interface implementation
- `app/routes/appointments.py` - Enhanced manage_services route and bulk update endpoint

#### Calendar View
- `app/templates/appointments/admin_calendar.html` - Redesigned with stylists as columns
- `app/routes/appointments.py` - Enhanced admin_appointments route with stylists data
- `test_calendar_view.py` - Calendar view test script

#### Page Templates
- `app/templates/main/index.html` - Added page title
- `app/templates/main/services.html` - Added page title
- `app/templates/main/customer_dashboard.html` - Added page title
- `app/templates/appointments/book.html` - Added page title
- `app/templates/appointments/my_appointments.html` - Added page title
- `app/templates/admin/dashboard.html` - Added page title

#### Testing
- `test_sidebar_navigation.py` - Navigation system test script
- `test_services_matrix.py` - Services matrix test script

### 🎨 User Interface Enhancements

#### Modern Design
- **Dark Sidebar**: Professional dark theme
- **Color Scheme**: Consistent brand colors
- **Typography**: Modern font stack
- **Icons**: Font Awesome icons throughout

#### Services Matrix Features
- **Matrix Layout**: Stylists vs services table
- **Checkbox Interface**: Easy assignment management
- **Service Details**: Duration, price, waiting time in headers
- **Stylist Information**: Names, usernames, role badges
- **Bulk Operations**: Save all assignments at once
- **Change Tracking**: Visual feedback for modifications

#### Calendar View Features
- **Stylist Columns**: Stylist names as column headers
- **Day Organization**: Days as row headers with time slots
- **Appointment Counts**: Visual counts per stylist per day
- **Status Indicators**: Color-coded appointment status
- **Time Slots**: Clear time-based organization
- **Responsive Design**: Works on all screen sizes

#### Interactive Elements
- **Hover Effects**: Visual feedback on navigation
- **Active States**: Current page highlighting
- **Smooth Transitions**: CSS animations
- **Loading States**: Visual feedback during actions

#### Accessibility
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: Proper ARIA labels
- **Focus Management**: Logical tab order
- **High Contrast**: Readable color combinations

### 🔧 New API Endpoints

#### Services Management
- `POST /appointments/services/bulk-update-associations` - Bulk update stylist-service associations

#### Enhanced Routes
- `GET /appointments/services` - Enhanced with matrix interface and stylist data

### 🚀 Migration Instructions

For users updating from previous versions:

1. **Stop the current container:**
   ```bash
   docker-compose down
   ```

2. **Update the codebase:**
   ```bash
   git pull origin main
   ```

3. **Rebuild and start:**
   ```bash
   docker-compose up --build
   ```

4. **Test the new features:**
   - Verify sidebar navigation works
   - Test services matrix interface
   - Check responsive design

### 🧪 Testing the New Features

#### Sidebar Navigation Testing
```bash
# 1. Test sidebar functionality
- Visit any page and verify sidebar appears
- Test collapse/expand button
- Verify responsive behavior on mobile
- Check role-based menu visibility

# 2. Test navigation links
- Verify all navigation links work
- Check active page highlighting
- Test mobile overlay functionality
```

#### Services Matrix Testing
```bash
# 1. Test matrix interface
- Navigate to Services management
- Verify matrix table appears
- Test checkbox functionality
- Check service details in headers

# 2. Test bulk operations
- Make changes to assignments
- Click "Save All Assignments"
- Verify progress modal appears
- Check success/error handling

# 3. Test change tracking
- Make changes and verify button state
- Test unsaved changes warning
- Verify changes are saved to database
```

#### Calendar View Testing
```bash
# 1. Test new calendar layout
- Navigate to All Appointments
- Verify stylist names as column headers
- Check day-based organization
- Test time slot display

# 2. Test appointment display
- Verify appointments appear in correct cells
- Check appointment counts in date headers
- Test color coding for status
- Verify responsive design

# 3. Test existing functionality
- Verify filters still work
- Check month view is preserved
- Test navigation controls
- Verify appointment list view
```

#### Verification Checklist
- [x] Sidebar navigation appears and functions correctly
- [x] Services matrix displays stylists and services
- [x] Checkboxes work for assignment management
- [x] Bulk save functionality works
- [x] Change tracking and visual feedback work
- [x] Responsive design works on all screen sizes
- [x] All existing functionality still works
- [x] Navigation links point to correct pages
- [x] Role-based menu visibility is correct
- [x] Calendar view shows stylists as columns
- [x] Appointment counts display correctly
- [x] Color coding for appointment status works

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

## 🆕 Latest Release: v1.3.0 - Stylist Calendar View Toggle & Enhanced UX

### 🎯 Overview
The latest release introduces enhanced calendar functionality with single-click view switching and improved user experience. This builds upon the previous Service Management Enhancements to provide seamless stylist workflow and salon coordination.

### ✨ New Features in v1.3.0

#### 1. **Stylist Calendar View Toggle**
- **Purpose**: Improve stylist workflow efficiency and salon coordination
- **Implementation**: Single-click switching between personal and global salon views
- **Features**:
  - Instant view switching without manual form submission
  - Auto-submit functionality for seamless transitions
  - Visual loading indicators during view changes
  - Enhanced user interface with tooltips and hints
  - Clean, intuitive design with removed redundant buttons

#### 2. **Enhanced User Experience**
- **Loading Feedback**: Spinner overlay during view transitions
- **Visual Indicators**: Clear badges showing current view state
- **Helpful Hints**: Tooltips explaining Personal vs Global view differences
- **Streamlined Interface**: Improved layout and responsive design
- **Accessibility**: Better user guidance and clear labeling

#### 3. **Technical Improvements**
- **JavaScript Auto-Submit**: Seamless form submission on view change
- **Enhanced Logging**: Better debugging and monitoring capabilities
- **Responsive Design**: Optimized for all screen sizes
- **Performance**: Reduced clicks and improved workflow efficiency

### 🔧 Technical Implementation

#### Enhanced Template Functionality
```javascript
// Auto-submit functionality for calendar view toggle
document.addEventListener('DOMContentLoaded', function() {
    const autoSubmitInputs = document.querySelectorAll('.auto-submit');
    
    autoSubmitInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            // Get the form and submit automatically
            const form = this.closest('form');
            if (form) {
                // Show loading indicator and submit
                setTimeout(function() {
                    form.submit();
                }, 150);
            }
        });
    });
});
```

#### UI/UX Improvements
- **Removed**: Redundant "Update View" button
- **Enhanced**: Layout with better column distribution
- **Added**: Visual indicators for current view state
- **Improved**: Responsive design and accessibility

### 🛣️ Enhanced Routes

#### Stylist Calendar View
- Enhanced `/appointments/stylist-appointments` route with improved parameter handling
- Added `calendar_view` parameter support (personal/global)
- Enhanced logging with stylist information for global view

### 🎨 Enhanced Templates

#### Stylist Calendar Interface
- Updated `app/templates/appointments/stylist_calendar.html` with:
  - Auto-submit radio buttons for view switching
  - Loading indicator overlay
  - Enhanced layout and styling
  - Tooltips and helpful hints
  - Visual feedback system

### 📁 New Files Created

#### Testing
- `test_calendar_view.py` - Comprehensive test script for calendar view functionality

### 🔄 Files Modified

#### Core Application Files
- `app/routes/appointments.py` - Enhanced stylist appointments route with view toggle support
- `app/templates/appointments/stylist_calendar.html` - Complete UI/UX overhaul

#### Dependencies
- `requirements.txt` - Added requests library for testing

### 🎨 User Interface Enhancements

#### Calendar View Management
- **Single-Click Switching**: Instant view changes without manual form submission
- **Visual Feedback**: Loading indicators and clear state indicators
- **Intuitive Design**: Clean interface with helpful hints and tooltips
- **Responsive Layout**: Optimized for all device sizes

#### Enhanced User Experience
- **Loading Indicators**: Visual feedback during view transitions
- **Tooltips**: Helpful information about each view type
- **Streamlined Interface**: Removed redundant buttons and improved layout
- **Accessibility**: Better user guidance and clear labeling

---

## 🆕 Previous Release: v1.2.0 - Stylist Service Associations & Custom Waiting Times

### 🎯 Overview
The previous release introduced advanced stylist service management with permission controls and custom waiting time support. This built upon the Service Management Enhancements to provide complete control over stylist-service relationships and timing flexibility.

### ✨ New Features in v1.2.0

#### 1. **Stylist-Service Associations**
- **Purpose**: Control which stylists can perform which services
- **Implementation**: New `StylistServiceAssociation` model for permission management
- **Features**:
  - Restrict stylist access to specific services
  - Prevent booking incompatible stylist-service combinations
  - Dynamic service filtering in booking forms
  - Complete CRUD interface for association management
- **API**: RESTful endpoint for getting stylist-allowed services

#### 2. **Custom Waiting Times for Stylist Timings**
- **Purpose**: Allow stylists to have custom waiting times per service
- **Implementation**: Enhanced `StylistServiceTiming` model with `custom_waiting_time` field
- **Features**:
  - Override service default waiting times per stylist
  - Auto-populate with service defaults in forms
  - Visual display of custom waiting times in management interface
  - Integration with booking system when stylist timing is enabled

#### 3. **Enhanced Booking Experience**
- **Dynamic Service Filtering**: Service selection filters based on stylist permissions
- **Custom Waiting Time Integration**: Custom waiting times applied when stylist timing is enabled
- **Improved Form Validation**: Better error handling and user experience
- **Auto-Populated Fields**: Service defaults automatically populate form fields

### 🔧 Technical Implementation

#### New Database Schema Changes
```sql
-- New StylistServiceAssociation table
CREATE TABLE stylist_service_association (
    id SERIAL PRIMARY KEY,
    stylist_id INTEGER REFERENCES user(id),
    service_id INTEGER REFERENCES service(id),
    is_allowed BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stylist_id, service_id)
);

-- Enhanced StylistServiceTiming table
ALTER TABLE stylist_service_timing ADD COLUMN custom_waiting_time INTEGER;
```

#### New Models
- **StylistServiceAssociation**: Manages stylist-service permission relationships
- **Enhanced StylistServiceTiming**: Added custom_waiting_time field

#### New Routes
- `/stylist-associations` - List all stylist associations
- `/stylist-associations/new` - Add new association
- `/stylist-associations/<id>/edit` - Edit existing association
- `/stylist-associations/<id>/delete` - Delete association
- `/api/stylist-services/<stylist_id>` - Get services allowed for a stylist
- `/api/service/<service_id>` - Get service details for form auto-population

#### New Templates
- `stylist_associations.html` - Management interface for associations
- `stylist_association_form.html` - Add/edit association form
- Enhanced `stylist_timing_form.html` - Added custom waiting time field
- Enhanced `stylist_timings.html` - Shows custom waiting times
- Enhanced `book.html` - Dynamic service filtering

### 🎨 User Interface Enhancements

#### Stylist Association Management
- **Dedicated Page**: "Stylist Associations" link in navigation for managers/owners
- **Permission Control**: Easy management of which stylists can perform which services
- **Visual Indicators**: Clear display of association status
- **Bulk Operations**: Efficient management of multiple associations

#### Enhanced Stylist Timing Management
- **Custom Waiting Time Field**: New field for stylist-specific waiting times
- **Auto-Population**: Service defaults automatically populate the waiting time field
- **Visual Display**: Custom waiting times shown in management interface
- **Integration**: Seamless integration with booking system

#### Enhanced Appointment Booking
- **Dynamic Service Filtering**: Only shows services the selected stylist can perform
- **Custom Waiting Time Support**: Uses custom waiting times when stylist timing is enabled
- **Improved UX**: Better form validation and error handling

### 📊 Business Benefits

#### For Salon Owners/Managers
- **Permission Control**: Ensure only qualified stylists perform specific services
- **Quality Assurance**: Prevent booking errors and service mismatches
- **Flexible Timing**: Allow stylists to set realistic waiting times
- **Better Scheduling**: More accurate appointment planning

#### For Stylists
- **Service Clarity**: Clear understanding of which services they can perform
- **Timing Flexibility**: Set custom waiting times based on their expertise
- **Professional Development**: Focus on services they're qualified for

#### For Customers
- **Accurate Bookings**: Only qualified stylists available for services
- **Better Experience**: More precise timing estimates
- **Service Quality**: Ensured expertise for each service type

### 🚀 Migration Guide

For users updating from previous versions, see the comprehensive [Migration Guide](MIGRATION_GUIDE.md) for step-by-step instructions.

### 🧪 Testing the New Features

#### Stylist Association Testing
```bash
# 1. Create stylist-service associations
- Navigate to Stylist Associations
- Add associations to control which stylists can perform which services
- Verify associations are saved correctly

# 2. Test booking with service filtering
- Book appointment and select a stylist
- Verify only allowed services appear in service selection
- Test with different stylists to ensure filtering works

# 3. Test custom waiting times
- Navigate to Stylist Timings
- Add custom waiting time to a stylist-service combination
- Verify waiting time auto-populates with service defaults
- Test booking with custom waiting times
```

#### Verification Checklist
- [ ] Stylist associations can be created and managed
- [ ] Service filtering works based on stylist permissions
- [ ] Custom waiting times can be added to stylist timings
- [ ] Custom waiting times auto-populate with service defaults
- [ ] Booking system uses custom waiting times when stylist timing is enabled
- [ ] Calendar view toggle works with single-click switching
- [ ] Loading indicators appear during view transitions
- [ ] Personal view shows only stylist's appointments
- [ ] Global view shows all salon appointments with stylist information
- [ ] API endpoints return correct data
- [ ] Navigation includes "Stylist Associations" link

---

## 🆕 Service Management Enhancements (v1.1.0)

### 🎯 Overview
The latest release introduces comprehensive Service Management Enhancements that provide advanced control over service timing, stylist-specific durations, and waiting time management. These features address the core requirements for professional salon operations.

### ✨ New Features

#### 1. **Service Waiting Times**
- **Purpose**: Track processing time for services like hair coloring
- **Implementation**: Added `waiting_time` field to Service model
- **Usage**: Managers can set waiting times (0-240 minutes) for services
- **Display**: Waiting times shown in service cards and booking forms

#### 2. **Stylist-Specific Service Timing**
- **Purpose**: Allow stylists to set custom durations for services they perform
- **Implementation**: New `StylistServiceTiming` model with unique stylist-service combinations
- **Features**:
  - Custom duration tracking per stylist per service
  - Visual time savings display (faster/slower than standard)
  - Active/inactive timing entries
  - Notes for timing explanations

#### 3. **Enhanced Appointment Booking**
- **Stylist Timing Selection**: Checkbox to use stylist's custom timing during booking
- **Multi-Service Support**: Book appointments with multiple services
- **Waiting Time Integration**: Automatic inclusion of waiting times in duration calculations
- **Timing Options**: Choose between standard service timing or stylist-specific timing

#### 4. **Advanced Service Management Interface**
- **Service Form Updates**: Added waiting time field with validation
- **Stylist Timing Management**: Dedicated interface for managing stylist timings
- **Visual Indicators**: Time savings badges and status indicators
- **Bulk Management**: Easy addition and editing of stylist timing entries

### 🔧 Technical Implementation

#### Database Schema Changes
```sql
-- New StylistServiceTiming table
CREATE TABLE stylist_service_timing (
    id SERIAL PRIMARY KEY,
    stylist_id INTEGER REFERENCES user(id),
    service_id INTEGER REFERENCES service(id),
    custom_duration INTEGER NOT NULL,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(stylist_id, service_id)
);

-- Added waiting_time column to Service table
ALTER TABLE service ADD COLUMN waiting_time INTEGER;
```

#### New Models
- **StylistServiceTiming**: Manages stylist-specific service durations
- **Enhanced Service Model**: Added waiting_time field and stylist timing relationships

#### New Routes
- `/stylist-timings` - List all stylist timings
- `/stylist-timings/new` - Add new stylist timing
- `/stylist-timings/<id>/edit` - Edit existing timing
- `/stylist-timings/<id>/delete` - Delete timing entry

#### New Templates
- `stylist_timings.html` - Management interface with time savings display
- `stylist_timing_form.html` - Add/edit stylist timing form
- Updated `service_form.html` - Added waiting time field
- Updated `services.html` - Shows waiting times in service cards
- Updated `book.html` - Added stylist timing checkbox

### 🎨 User Interface Enhancements

#### Service Management
- **Waiting Time Field**: New field in service creation/editing forms
- **Service Cards**: Display waiting time information alongside duration and price
- **Validation**: Proper validation for waiting time (0-240 minutes)

#### Stylist Timing Management
- **Dedicated Page**: "Stylist Timings" link in navigation for managers/owners
- **Time Savings Display**: Visual indicators showing time saved/extra time needed
- **Status Management**: Active/inactive timing entries
- **Bulk Operations**: Easy management of multiple timing entries

#### Appointment Booking
- **Stylist Timing Checkbox**: Option to use stylist's custom timing
- **Enhanced Service Rows**: Improved layout with timing options
- **Dynamic Duration**: Automatic duration updates based on timing selection

### 📊 Business Benefits

#### For Salon Owners/Managers
- **Accurate Scheduling**: Better appointment duration estimates
- **Stylist Optimization**: Track which stylists are faster/slower
- **Service Planning**: Understand actual service timing requirements
- **Revenue Optimization**: More accurate booking slots

#### For Stylists
- **Personalized Timing**: Set realistic durations for their work style
- **Better Scheduling**: Avoid overbooking or underbooking
- **Performance Tracking**: See how their timing compares to standard

#### For Customers
- **Accurate Appointments**: More precise appointment durations
- **Better Experience**: Reduced waiting times and better scheduling
- **Service Transparency**: Clear understanding of service timing

### 🚀 Migration Guide

For users updating from previous versions, see the comprehensive [Migration Guide](MIGRATION_GUIDE.md) for step-by-step instructions.

### 🧪 Testing the New Features

#### Service Management Testing
```bash
# 1. Add waiting time to a service
- Navigate to Services > Edit Service
- Add waiting time (e.g., 30 minutes for color services)
- Save and verify waiting time appears in service list

# 2. Create stylist timing entries
- Navigate to Stylist Timings
- Add custom timing for a stylist-service combination
- Verify time savings are calculated and displayed

# 3. Test appointment booking with new features
- Book appointment with multiple services
- Enable stylist timing checkbox
- Verify duration calculations include waiting times
```

#### Verification Checklist
- [ ] Waiting times can be added to services
- [ ] Stylist timings can be created and managed
- [ ] Appointment booking includes timing options
- [ ] Duration calculations work correctly
- [ ] Calendar displays multi-service appointments
- [ ] Navigation includes "Stylist Timings" link

### 🔮 Future Enhancements

#### Planned Features
- **Historical Timing Analysis**: Track timing trends over time
- **Automatic Timing Suggestions**: AI-powered timing recommendations
- **Service Combinations**: Pre-defined service packages with timing
- **Advanced Reporting**: Detailed timing and efficiency reports
- **Mobile App Integration**: Timing management on mobile devices

### 🆕 Recent Updates (Previous Development Session)

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
- **Enhanced Service Management**: Add, edit, and manage salon services with waiting times
- **Stylist Timing Management**: Set custom durations for stylist-service combinations
- **Status Management**: Update appointment statuses with notes
- **Advanced Booking**: Book appointments with multiple services and custom timing

### Database Models

#### Service
- `name`: Service name (e.g., "Haircut & Style")
- `description`: Detailed service description
- `duration`: Duration in minutes
- `waiting_time`: Optional waiting/processing time in minutes (e.g., for color processing)
- `price`: Service price in GBP
- `is_active`: Whether the service is available for booking

#### StylistServiceTiming
- `stylist_id`: Reference to the stylist
- `service_id`: Reference to the service
- `custom_duration`: Custom duration in minutes for this stylist-service combination
- `notes`: Optional notes about the timing
- `is_active`: Whether this timing entry is active

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

1. **Database Migration**: Run the migration scripts to set up the database schema:
   ```bash
   # Run multi-service appointment migration
   docker exec -it salon-ese-web-1 python migrate_appointments_multiservice.py
   
   # Run stylist timings migration
   docker exec -it salon-ese-web-1 python migrate_stylist_timings.py
   ```

2. **Initialize Services**: Run the service initialization script:
   ```bash
   python init_services.py
   ```

3. **Create Stylist Users**: Use the admin panel to create users with the 'stylist' role

4. **Create Customer Users**: Users can register as customers or be created via admin panel

5. **Configure Service Timings**: 
   - Add waiting times to services (e.g., color processing time)
   - Create stylist-specific timing entries for faster/slower stylists
   - Test appointment booking with timing options

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
- `GET /appointments/stylist-timings` - Manage stylist service timings
- `GET/POST /appointments/stylist-timings/new` - Add new stylist timing
- `GET/POST /appointments/stylist-timings/<id>/edit` - Edit stylist timing
- `POST /appointments/stylist-timings/<id>/delete` - Delete stylist timing

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
├── migrate_appointments_multiservice.py  # Multi-service appointment migration
├── migrate_stylist_timings.py           # Stylist timing migration
├── MIGRATION_GUIDE.md    # Migration instructions for users
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