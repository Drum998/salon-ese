# Salon ESE - Feature Documentation

## 🎯 **Overview**

This document provides detailed documentation for all major features and systems in the Salon ESE project, including the HR System, Holiday Management System, Test Runner, and other key functionalities.

## 🏢 **HR System Integration**

### **Overview**
The HR System Integration provides comprehensive cost calculation, employment details management, and financial tracking capabilities for salon operations.

### **Key Features**

#### **Employment Details Management**
- **Start/End Dates**: Track employment periods with start and end dates
- **Compensation Models**: Support for both employed and self-employed staff
- **Rate Management**: Hourly rates for employed staff, commission rates for self-employed
- **Base Salary**: Annual base salary tracking for employed staff

#### **Cost Calculations**
- **Appointment Cost Tracking**: Automatic calculation of costs for each appointment
- **Revenue Analysis**: Track service revenue, stylist costs, and salon profit
- **Performance Metrics**: Calculate profit margins and commission efficiency
- **Financial Reporting**: Comprehensive financial overview and analytics

#### **Database Models**

##### **Enhanced EmploymentDetails Model**
```python
class EmploymentDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    employment_type = db.Column(db.String(20), nullable=False)  # 'employed' or 'self_employed'
    
    # HR System Integration - New Fields
    start_date = db.Column(db.Date, nullable=False, default=datetime.now().date())
    end_date = db.Column(db.Date, nullable=True)  # Null for current employees
    hourly_rate = db.Column(db.Numeric(8, 2), nullable=True)  # For employed staff
    commission_rate = db.Column(db.Numeric(5, 2), nullable=True)  # For self-employed
    base_salary = db.Column(db.Numeric(10, 2), nullable=True)  # For employed staff
    
    # Methods
    def calculate_hourly_cost(self, hours):
        """Calculate cost for hourly employees"""
        if not self.is_employed or not self.hourly_rate:
            return 0
        return float(self.hourly_rate) * hours
    
    def calculate_commission_cost(self, service_revenue):
        """Calculate cost for commission-based employees"""
        if not self.is_self_employed or not self.commission_rate:
            return 0
        return float(service_revenue) * (float(self.commission_rate) / 100)
```

##### **AppointmentCost Model**
```python
class AppointmentCost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    stylist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Cost breakdown
    service_revenue = db.Column(db.Numeric(10, 2), nullable=False)
    stylist_cost = db.Column(db.Numeric(10, 2), nullable=False)
    salon_profit = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Calculation details
    calculation_method = db.Column(db.String(20), nullable=False)  # 'hourly' or 'commission'
    hours_worked = db.Column(db.Numeric(4, 2), nullable=True)
    commission_amount = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Enhanced Commission System
    commission_breakdown = db.Column(db.JSON, nullable=True)
    billing_method = db.Column(db.String(20), nullable=True)
    billing_elements_applied = db.Column(db.JSON, nullable=True)
```

#### **HR Service Layer**

##### **HRService**
```python
class HRService:
    @staticmethod
    def calculate_appointment_cost(appointment_id):
        """Calculate cost breakdown for an appointment"""
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return None
        
        employment = EmploymentDetails.query.filter_by(user_id=appointment.stylist_id).first()
        if not employment:
            return None
        
        # Calculate service revenue
        service_revenue = sum(link.service.price for link in appointment.services_link)
        
        # Calculate stylist cost based on employment type
        if employment.is_employed:
            hours_worked = appointment.duration_minutes / 60
            stylist_cost = employment.calculate_hourly_cost(hours_worked)
            calculation_method = 'hourly'
        else:
            stylist_cost = employment.calculate_commission_cost(service_revenue)
            calculation_method = 'commission'
        
        salon_profit = service_revenue - stylist_cost
        
        return {
            'service_revenue': service_revenue,
            'stylist_cost': stylist_cost,
            'salon_profit': salon_profit,
            'calculation_method': calculation_method
        }
    
    @staticmethod
    def get_stylist_performance_report(stylist_id, start_date, end_date):
        """Generate performance report for a stylist"""
        appointments = Appointment.query.filter(
            Appointment.stylist_id == stylist_id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).all()
        
        total_revenue = 0
        total_cost = 0
        total_appointments = len(appointments)
        
        for appointment in appointments:
            cost = AppointmentCost.query.filter_by(appointment_id=appointment.id).first()
            if cost:
                total_revenue += float(cost.service_revenue)
                total_cost += float(cost.stylist_cost)
        
        return {
            'total_appointments': total_appointments,
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_profit': total_revenue - total_cost,
            'average_revenue_per_appointment': total_revenue / total_appointments if total_appointments > 0 else 0
        }
```

#### **Admin Interfaces**

##### **HR Dashboard**
- **Route**: `/admin/hr-dashboard`
- **Features**:
  - Financial summary cards
  - Employment status overview
  - Cost breakdown charts
  - Date range filters
  - Employment details table

##### **Appointment Costs View**
- **Route**: `/admin/hr/appointment-costs`
- **Features**:
  - Detailed cost breakdown table
  - Filtering capabilities
  - Pagination support
  - Export functionality

##### **Stylist Earnings Reports**
- **Route**: `/admin/hr/stylist-earnings`
- **Features**:
  - Earnings summary cards
  - Stylist ranking table
  - Performance metrics
  - Date range filtering

## 🏖️ **Holiday Management System**

### **Overview**
The Holiday Management System provides a complete solution for staff holiday requests and management, including automatic entitlement calculations based on work patterns and a streamlined approval workflow.

### **Key Features**

#### **Staff Holiday Request System**
- **Route**: `/holiday-request`
- **Purpose**: Allow stylists to submit holiday requests
- **Features**:
  - Date range selection with validation
  - Automatic calculation of requested days
  - Current quota display
  - Recent requests history
  - Form validation and error handling

#### **Admin Holiday Management**
- **Routes**: 
  - `/admin/holiday-requests` - View all requests
  - `/admin/holiday-requests/<id>` - View individual request
  - `/admin/holiday-requests/<id>/approve` - Approve/reject request
  - `/admin/holiday-quotas` - View all quotas
  - `/admin/holiday-quotas/<user_id>` - View user-specific summary
- **Purpose**: Complete admin control over holiday management
- **Features**:
  - Request filtering and pagination
  - Approval workflow with notes
  - Quota management and tracking
  - Usage statistics and alerts
  - Integration with HR dashboard

#### **Automatic Entitlement Calculations**
- **Based on**: Work patterns and weekly hours
- **UK Employment Law**: 5.6 weeks per year (28 days for full-time)
- **Calculation**: Proportional to weekly hours
- **Integration**: Automatic calculation when work patterns change

### **Database Models**

#### **HolidayQuota Model**
```python
class HolidayQuota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_hours_per_week = db.Column(db.Integer, nullable=False)
    holiday_days_entitled = db.Column(db.Integer, nullable=False)
    holiday_days_taken = db.Column(db.Integer, default=0)
    holiday_days_remaining = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    # Relationships
    user = db.relationship('User', backref='holiday_quotas')
    
    @classmethod
    def calculate_entitlement(cls, hours_per_week):
        """Calculate holiday entitlement based on UK employment law"""
        if hours_per_week >= 37.5:  # Full-time
            return 28
        elif hours_per_week >= 20:  # Part-time
            return int((hours_per_week / 37.5) * 28)
        else:  # Reduced hours
            return int((hours_per_week / 37.5) * 28)
    
    def update_remaining_days(self):
        """Update remaining days based on taken days"""
        self.holiday_days_remaining = self.holiday_days_entitled - self.holiday_days_taken
```

#### **HolidayRequest Model**
```python
class HolidayRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='holiday_requests')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approved_holidays')
    
    def approve(self, approved_by_user):
        """Approve the holiday request"""
        self.status = 'approved'
        self.approved_by_id = approved_by_user.id
        self.approved_at = uk_utcnow()
        
        # Update holiday quota
        quota = HolidayQuota.query.filter_by(
            user_id=self.user_id, 
            year=self.start_date.year
        ).first()
        
        if quota:
            quota.holiday_days_taken += self.days_requested
            quota.update_remaining_days()
    
    def reject(self, rejected_by_user, notes=None):
        """Reject the holiday request"""
        self.status = 'rejected'
        self.approved_by_id = rejected_by_user.id
        self.approved_at = uk_utcnow()
        if notes:
            self.notes = notes
```

### **Service Layer**

#### **HolidayService**
```python
class HolidayService:
    @staticmethod
    def calculate_holiday_entitlement(hours_per_week):
        """Calculate holiday entitlement based on UK employment law"""
        if hours_per_week >= 37.5:  # Full-time
            return 28
        elif hours_per_week >= 20:  # Part-time
            return int((hours_per_week / 37.5) * 28)
        else:  # Reduced hours
            return int((hours_per_week / 37.5) * 28)

    @staticmethod
    def get_or_create_holiday_quota(user_id, year=None):
        """Get or create holiday quota for user"""
        if year is None:
            year = datetime.now().year
        
        quota = HolidayQuota.query.filter_by(user_id=user_id, year=year).first()
        if not quota:
            # Get user's work pattern to calculate hours
            work_pattern = WorkPattern.query.filter_by(user_id=user_id, is_active=True).first()
            if work_pattern:
                hours_per_week = work_pattern.get_weekly_hours()
                entitled_days = HolidayService.calculate_holiday_entitlement(hours_per_week)
                
                quota = HolidayQuota(
                    user_id=user_id,
                    year=year,
                    total_hours_per_week=hours_per_week,
                    holiday_days_entitled=entitled_days,
                    holiday_days_remaining=entitled_days
                )
                db.session.add(quota)
                db.session.commit()
        
        return quota

    @staticmethod
    def submit_holiday_request(user_id, start_date, end_date, notes=None):
        """Submit a new holiday request"""
        # Calculate days requested
        days_requested = (end_date - start_date).days + 1
        
        # Check if user has enough remaining days
        quota = HolidayService.get_or_create_holiday_quota(user_id, start_date.year)
        if quota.holiday_days_remaining < days_requested:
            raise ValueError(f"Insufficient holiday days. Available: {quota.holiday_days_remaining}, Requested: {days_requested}")
        
        # Create request
        request = HolidayRequest(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            days_requested=days_requested,
            notes=notes
        )
        
        db.session.add(request)
        db.session.commit()
        
        return request
```

### **Admin Interfaces**

#### **Holiday Requests Management**
- **Route**: `/admin/holiday-requests`
- **Features**:
  - View all holiday requests with filtering
  - Pagination support
  - Status-based filtering (pending, approved, rejected)
  - Date range filtering
  - Bulk actions

#### **Individual Request Management**
- **Route**: `/admin/holiday-requests/<id>`
- **Features**:
  - Detailed request view
  - Approval/rejection workflow
  - Notes and comments
  - Integration with quota updates

#### **Holiday Quotas Management**
- **Route**: `/admin/holiday-quotas`
- **Features**:
  - View all staff holiday quotas
  - Year-based filtering
  - Usage statistics
  - Manual quota adjustments

## 🧪 **Comprehensive Test Runner**

### **Overview**
The Comprehensive Test Runner is a powerful testing system designed to organize and execute all tests in the Salon ESE project efficiently.

### **Key Features**

#### **Organized Test Categories**
- **Core Tests**: Database connectivity, models, authentication, timezone handling
- **Admin Tests**: Admin panel and user management tests
- **HR Tests**: HR system and employment management tests
- **UI Tests**: User interface and navigation tests
- **Analytics Tests**: Analytics and reporting system tests
- **Integration Tests**: Integration and system-wide tests

#### **Test Presets**
- **Smoke Tests**: Quick validation of basic functionality
- **Development Tests**: Comprehensive testing during active development
- **Production Tests**: Full system validation before deployment

#### **Configuration Management**
- Easy enable/disable of individual tests
- Configurable timeouts and output settings
- Docker integration for containerized environments

### **Usage**

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

### **Test Categories Details**

#### **Core Tests**
- **Files**: `test_db.py`, `test_models.py`, `test_new_models.py`, `test_template_filter.py`, `test_timezone.py`, `test_auth.py`
- **Purpose**: Validate core system functionality
- **Coverage**: Database operations, model relationships, authentication, timezone handling

#### **Admin Tests**
- **Files**: `test_admin.py`, `tests/test_auth.py`
- **Purpose**: Validate admin panel functionality
- **Coverage**: User management, role management, admin forms, authorization

#### **HR Tests**
- **Files**: `test_hr_system.py`, `test_commission_system.py`, `test_analytics_system.py`, `tests/test_salon_settings.py`, `tests/test_work_patterns.py`, `tests/test_employment_details.py`
- **Purpose**: Validate HR system functionality
- **Coverage**: Employment details, cost calculations, commission tracking, work patterns

#### **UI Tests**
- **Files**: `test_sidebar_navigation.py`, `test_services_matrix.py`, `test_single_block_css.py`, `test_calendar_navigation.py`, `test_calendar_view.py`, `test_click_to_book.py`, `test_appointment_visibility.py`, `test_appointment_display.py`
- **Purpose**: Validate user interface functionality
- **Coverage**: Navigation, calendar views, appointment display, services matrix

#### **Analytics Tests**
- **Files**: `test_analytics_system.py`, `test_commission_system.py`
- **Purpose**: Validate analytics and reporting functionality
- **Coverage**: Analytics calculations, commission reporting, performance metrics

#### **Integration Tests**
- **Files**: `test_salon_hours_integration.py`, `debug_tests.py`
- **Purpose**: Validate system integration
- **Coverage**: System-wide functionality, salon hours integration, debug scenarios

## 🎨 **Advanced Calendar & Seniority System**

### **Overview**
The Advanced Calendar & Seniority System provides enhanced calendar functionality with seniority-based stylist hierarchy and professional time management features.

### **Key Features**

#### **24-Hour Time Format**
- All appointment times display in professional 24-hour format
- Consistent time display across all interfaces
- Enhanced clarity for professional salon operations

#### **Calendar Filter Persistence**
- Calendar filter options persist across navigation and page loads
- Maintains user preferences for view type, stylist, status, and role filters
- Improved user experience with consistent filtering

#### **Enhanced Week View**
- Optimized for large numbers of stylists with horizontal scrolling
- Compact layout with narrower columns and optimized spacing
- Better information density for professional use

#### **Seniority-Based Stylist Hierarchy**
- **Five-Tier System**: Owner → Manager → Senior Stylist → Stylist → Junior Stylist
- **Color-Coded System**: Visual distinction with blue gradient from dark (Senior) to light (Junior)
- **Automatic Ordering**: Column ordering by seniority level in calendar views
- **Role-Based Filtering**: Filter calendar view by specific seniority roles

### **Technical Implementation**

#### **Seniority Role System**
```python
# Seniority hierarchy implementation
SENIORITY_ORDER = {
    'owner': 1,
    'manager': 2, 
    'senior_stylist': 3,
    'stylist': 4,
    'junior_stylist': 5
}

# Role-based color coding
ROLE_COLORS = {
    'owner': '#dc3545',      # Red
    'manager': '#fd7e14',    # Orange  
    'senior_stylist': '#0d6efd',  # Dark Blue
    'stylist': '#0dcaf0',    # Medium Blue
    'junior_stylist': '#87ceeb'   # Light Blue
}
```

#### **Calendar Filter Persistence**
```python
# Filter state preservation
def admin_appointments():
    view_type = request.args.get('view_type', 'month')
    stylist_id = request.args.get('stylist_id', '')
    status_filter = request.args.get('status', '')
    role_filter = request.args.get('role_filter', '')
    
    # Populate form with current filter state
    form.view_type.data = view_type
    form.stylist_id.data = stylist_id
    form.status.data = status_filter
```

#### **Seniority-Based Ordering**
```python
# SQLAlchemy case statement for seniority ordering
from sqlalchemy import case

stylists = User.query.join(User.roles).filter(
    Role.name.in_(['stylist', 'manager', 'owner', 'senior_stylist', 'junior_stylist'])
).order_by(
    case(
        (Role.name == 'owner', 1),
        (Role.name == 'manager', 2),
        (Role.name == 'senior_stylist', 3),
        (Role.name == 'stylist', 4),
        (Role.name == 'junior_stylist', 5),
        else_=6
    )
).all()
```

### **Enhanced CSS for Calendar Views**
```css
/* Horizontal scrolling for week view */
.calendar-container {
    overflow-x: auto;
    min-width: 800px;
}

/* Role-based color coding */
.stylist-column.owner { background-color: #dc3545; }
.stylist-column.manager { background-color: #fd7e14; }
.stylist-column.senior_stylist { background-color: #0d6efd; }
.stylist-column.stylist { background-color: #0dcaf0; }
.stylist-column.junior_stylist { background-color: #87ceeb; }

/* Compact layout */
.calendar-slot {
    height: 10px;
    margin: 1px;
}

.appointment-block {
    height: calc(rowspan * 20px);
    margin: 1px;
}
```

## 🔧 **Commission Calculation System**

### **Overview**
The Commission Calculation System provides advanced commission tracking and billing element management for salon operations.

### **Key Features**

#### **Enhanced Commission Tracking**
- **Commission Breakdown**: Detailed tracking of commission calculations
- **Billing Elements**: Support for multiple billing elements (Color, Electric, Styling, Treatment, Other)
- **Billing Methods**: Support for both salon billing and stylist billing
- **Performance Metrics**: Commission efficiency and performance analytics

#### **Billing Elements Management**
- **Configurable Elements**: Add, edit, and manage billing elements
- **Percentage-Based**: Each element has a configurable percentage
- **Active/Inactive**: Enable or disable billing elements as needed
- **Total Percentage Tracking**: Monitor total billing element percentages

### **Database Models**

#### **BillingElement Model**
```python
class BillingElement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., 'color', 'electric'
    percentage = db.Column(db.Numeric(5, 2), nullable=False)  # e.g., 25.00 for 25%
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    def __repr__(self):
        return f'<BillingElement {self.name}>'
    
    @classmethod
    def get_active_elements(cls):
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def get_total_percentage(cls):
        elements = cls.get_active_elements()
        return sum(float(element.percentage) for element in elements)
```

#### **Enhanced AppointmentCost Model**
```python
class AppointmentCost(db.Model):
    # ... existing fields ...
    
    # Enhanced Commission System - New Fields
    commission_breakdown = db.Column(db.JSON, nullable=True)  # Detailed commission breakdown
    billing_method = db.Column(db.String(20), nullable=True)  # 'salon_bills' or 'stylist_bills'
    billing_elements_applied = db.Column(db.JSON, nullable=True)  # Billing elements breakdown
    
    @property
    def commission_performance_metrics(self):
        """Calculate commission performance metrics"""
        if not self.commission_breakdown:
            return None
            
        breakdown = self.commission_breakdown
        metrics = {
            'total_commission': breakdown.get('total_commission', 0),
            'commission_percentage': breakdown.get('commission_percentage', 0),
            'service_revenue': breakdown.get('service_revenue', 0),
            'calculation_method': breakdown.get('calculation_method', 'percentage'),
            'commission_efficiency': 0
        }
        
        # Calculate commission efficiency (commission as % of revenue)
        if metrics['service_revenue'] > 0:
            metrics['commission_efficiency'] = (metrics['total_commission'] / metrics['service_revenue']) * 100
            
        return metrics
    
    @property
    def billing_elements_summary(self):
        """Get summary of billing elements applied"""
        if not self.billing_elements_applied:
            return None
            
        elements = self.billing_elements_applied
        summary = {
            'total_elements': len(elements),
            'total_percentage': sum(element.get('percentage', 0) for element in elements.values()),
            'elements': elements
        }
        
        return summary
```

### **Service Layer**

#### **Commission Calculation Service**
```python
class CommissionService:
    @staticmethod
    def calculate_commission_breakdown(appointment_id, billing_method='salon_bills'):
        """Calculate detailed commission breakdown for an appointment"""
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return None
        
        # Get employment details
        employment = EmploymentDetails.query.filter_by(user_id=appointment.stylist_id).first()
        if not employment or not employment.is_self_employed:
            return None
        
        # Calculate service revenue
        service_revenue = sum(link.service.price for link in appointment.services_link)
        
        # Get billing elements
        billing_elements = BillingElement.get_active_elements()
        
        # Calculate commission breakdown
        commission_breakdown = {
            'service_revenue': service_revenue,
            'commission_percentage': float(employment.commission_rate),
            'calculation_method': 'percentage',
            'billing_method': billing_method,
            'billing_elements': {},
            'total_commission': 0
        }
        
        # Apply billing elements
        for element in billing_elements:
            element_amount = service_revenue * (float(element.percentage) / 100)
            commission_breakdown['billing_elements'][element.name] = {
                'percentage': float(element.percentage),
                'amount': element_amount
            }
            commission_breakdown['total_commission'] += element_amount
        
        return commission_breakdown
```

### **Admin Interfaces**

#### **Commission Reports**
- **Route**: `/admin/commission-reports`
- **Features**:
  - Commission performance analytics
  - Stylist ranking by commission
  - Date range filtering
  - Export functionality

#### **Billing Elements Management**
- **Route**: `/admin/billing-elements`
- **Features**:
  - Add, edit, and delete billing elements
  - Percentage configuration
  - Active/inactive status management
  - Total percentage monitoring

## 📊 **Analytics System**

### **Overview**
The Analytics System provides comprehensive reporting and analytics for salon operations, including financial metrics, staff performance, and business insights.

### **Key Features**

#### **Financial Analytics**
- **Revenue Tracking**: Monitor service revenue and trends
- **Cost Analysis**: Track stylist costs and salon expenses
- **Profit Margins**: Calculate and monitor profit margins
- **Performance Metrics**: Key performance indicators for business health

#### **Staff Performance Analytics**
- **Stylist Rankings**: Performance rankings based on various metrics
- **Commission Analytics**: Commission trends and performance analysis
- **Utilization Tracking**: Staff utilization and capacity planning
- **Holiday Analytics**: Holiday trends and conflict detection

#### **Business Intelligence**
- **Trend Analysis**: Identify trends in appointments and revenue
- **Seasonal Patterns**: Analyze seasonal variations in business
- **Customer Insights**: Customer behavior and preferences analysis
- **Operational Efficiency**: Identify areas for operational improvement

### **Service Layer**

#### **AnalyticsService**
```python
class AnalyticsService:
    @staticmethod
    def get_executive_dashboard_data(start_date=None, end_date=None):
        """Get high-level KPIs for executive dashboard"""
        # Revenue and commission metrics
        revenue_data = HRService.calculate_salon_commission_summary(start_date, end_date)
        
        # Staff metrics
        total_stylists = User.query.join(User.roles).filter(Role.name == 'stylist').count()
        active_stylists = Appointment.query.filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).with_entities(Appointment.stylist_id).distinct().count()
        
        # Holiday metrics
        holiday_requests = HolidayRequest.query.filter(
            HolidayRequest.start_date >= start_date,
            HolidayRequest.start_date <= end_date
        ).count()
        
        return {
            'revenue': revenue_data.get('total_revenue', 0),
            'commission': revenue_data.get('total_commission', 0),
            'total_stylists': total_stylists,
            'active_stylists': active_stylists,
            'staff_utilization': (active_stylists / total_stylists * 100) if total_stylists > 0 else 0,
            'holiday_requests': holiday_requests,
            'total_appointments': total_appointments
        }
    
    @staticmethod
    def analyze_holiday_trends(start_date=None, end_date=None):
        """Analyze holiday request patterns and trends"""
        # Monthly holiday request trends with PostgreSQL compatibility
        monthly_trends = db.session.query(
            func.to_char(HolidayRequest.start_date, 'YYYY-MM').label('month'),
            func.count(HolidayRequest.id).label('total_requests'),
            func.count(case([(HolidayRequest.status == 'approved', 1)])).label('approved'),
            func.count(case([(HolidayRequest.status == 'rejected', 1)])).label('rejected')
        ).filter(
            HolidayRequest.start_date >= start_date,
            HolidayRequest.start_date <= end_date
        ).group_by(
            func.to_char(HolidayRequest.start_date, 'YYYY-MM')
        ).order_by('month').all()
        
        # Staff holiday utilization with proper foreign key joins
        staff_utilization = db.session.query(
            User.username,
            func.count(HolidayRequest.id).label('total_requests'),
            func.count(case([(HolidayRequest.status == 'approved', 1)])).label('approved_requests'),
            func.avg(HolidayRequest.days_requested).label('avg_duration')
        ).join(
            HolidayRequest, User.id == HolidayRequest.user_id
        ).filter(
            HolidayRequest.start_date >= start_date,
            HolidayRequest.start_date <= end_date
        ).group_by(User.id, User.username).all()
        
        return {
            'monthly_trends': [...],
            'staff_utilization': [...],
            'conflicts': conflicts
        }
    
    @staticmethod
    def analyze_commission_trends(start_date=None, end_date=None):
        """Analyze commission performance trends"""
        # Monthly commission trends with proper Decimal handling
        monthly_commission = db.session.query(
            func.to_char(Appointment.appointment_date, 'YYYY-MM').label('month'),
            func.sum(AppointmentCost.service_revenue).label('total_revenue'),
            func.sum(AppointmentCost.commission_amount).label('total_commission')
        ).join(
            AppointmentCost, Appointment.id == AppointmentCost.appointment_id
        ).filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date,
            AppointmentCost.commission_amount > 0
        ).group_by(
            func.to_char(Appointment.appointment_date, 'YYYY-MM')
        ).order_by('month').all()
        
        return {
            'monthly_trends': [...],
            'stylist_rankings': [...],
            'billing_elements': element_performance
        }
    
    @staticmethod
    def calculate_staff_utilization(start_date=None, end_date=None):
        """Calculate comprehensive staff utilization metrics"""
        # Staff utilization with proper Decimal to float conversion
        for stylist in stylists:
            total_revenue = sum(
                float(AppointmentCost.query.filter_by(appointment_id=appointment.id).first().service_revenue)
                for appointment in appointments
                if AppointmentCost.query.filter_by(appointment_id=appointment.id).first()
            )
            
            revenue_per_hour = (total_revenue / actual_hours) if actual_hours > 0 else 0
            
        return {
            'staff_utilization': utilization_data,
            'avg_utilization_rate': avg_rate,
            'total_revenue': total_revenue
        }
```

### **Admin Interfaces**

#### **Analytics Dashboard**
- **Route**: `/admin/analytics/dashboard`
- **Features**:
  - Executive dashboard with high-level KPIs
  - Revenue, commission, and staff utilization metrics
  - Date range filtering for all analytics
  - Interactive charts and visualizations
  - Navigation to detailed analytics modules

#### **Holiday Trends Analytics**
- **Route**: `/admin/analytics/holiday-trends`
- **Features**:
  - Monthly holiday request trends with approval/rejection rates
  - Staff holiday utilization statistics
  - Automated conflict detection for overlapping holidays
  - Interactive bar charts for data visualization
  - Date range filtering and export capabilities

#### **Commission Trends Analytics**
- **Route**: `/admin/analytics/commission-trends`
- **Features**:
  - Monthly revenue and commission performance trends
  - Stylist performance rankings with efficiency metrics
  - Billing element performance analysis
  - Summary statistics with total revenue and commission rates
  - Interactive line charts with dual-axis support

#### **Staff Utilization Analytics**
- **Route**: `/admin/analytics/staff-utilization`
- **Features**:
  - Staff utilization rates with color-coded progress bars
  - Capacity planning recommendations based on demand analysis
  - Revenue per hour and appointment duration metrics
  - Work pattern integration for scheduled vs actual hours
  - Capacity analysis with over/under capacity alerts

## 🔗 **Integration Features**

### **Cross-System Integration**
- **HR-Appointment Integration**: Automatic cost calculations on appointment booking
- **Holiday-Work Pattern Integration**: Automatic entitlement calculations
- **Analytics-All Systems**: Comprehensive reporting across all systems
- **Commission-Billing Integration**: Detailed commission tracking with billing elements

### **Data Consistency**
- **Automatic Updates**: Systems automatically update related data
- **Validation**: Cross-system validation ensures data consistency
- **Audit Trail**: Complete audit trail for all system changes
- **Error Handling**: Comprehensive error handling and recovery

This comprehensive feature documentation provides detailed information about all major systems and features in the Salon ESE project, enabling developers and users to understand and utilize the full capabilities of the system.
