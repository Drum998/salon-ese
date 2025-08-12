# Quick Update Guide - Complete System Update (HR System to Advanced Analytics)

## Overview
This guide provides the commands needed to update the Salon ESE system from the HR System migration to the current Advanced Analytics System (v2.5.0). This covers all updates from the last major migration point.

## Fresh Installation (Nuclear Reset)

If you want to start completely fresh with a clean database and comprehensive test data:

### 1. Nuclear Database Reset
```bash
# Stop containers
docker-compose down

# Remove the database volume (this deletes ALL data)
docker volume rm salon-ese_postgres_data

# Start containers fresh
docker-compose up -d

# Wait for database to be ready
docker-compose logs -f db
# (Wait until you see "database system is ready to accept connections")
```

### 2. Initialize Services (Required First)
```bash
docker exec -it salon-ese-web-1 python init_services.py
```

### 3. Apply Commission System Migration
```bash
docker exec -it salon-ese-web-1 python migrate_commission_system.py
```

### 4. Add Comprehensive Test Data
```bash
docker exec -it salon-ese-web-1 python add_test_users.py
```

### 5. Verify Installation
```bash
# Check that test data was created
docker exec -it salon-ese-web-1 python -c "
from app import create_app
from app.models import User, Service, EmploymentDetails, Appointment
app = create_app()
with app.app_context():
    print(f'Users: {User.query.count()}')
    print(f'Services: {Service.query.count()}')
    print(f'Employment Details: {EmploymentDetails.query.count()}')
    print(f'Appointments: {Appointment.query.count()}')
"
```

**Test Login Credentials:**
- **Manager**: `manager_1` / `12345678`
- **Stylists**: `stylist_1`, `stylist_2`, `stylist_3` / `12345678`
- **Customers**: `cust_1`, `cust_2`, `cust_3`, `cust_4`, `cust_5` / `12345678`

## Prerequisites
- Your system should have completed the HR System migration (`migrate_hr_system.py`)
- Docker containers should be running
- Database should be accessible

## Update Commands (Run in Order)

### 0. Get lates version from Github
```bash
git pull origin main
```

### 1. Apply Commission System Migration
```bash
docker exec -it salon-ese-web-1 python migrate_commission_system.py
```

**What this does:**
- Adds `commission_breakdown`, `billing_method`, and `billing_elements_applied` columns to `appointment_cost` table
- Creates default billing elements (Color, Electric, Styling, Treatment, Other)
- Updates existing appointment costs with billing method and commission breakdown

### 2. Restart Application (Required after Commission Migration)
```bash
docker-compose restart web
```

### 3. Verify Commission System (Optional)
```bash
docker exec -it salon-ese-web-1 python test_commission_system.py
```

### 4. Fix Analytics Service (Critical - Fixes AttributeError)
```bash
docker exec -it salon-ese-web-1 python -c "
from app.services.analytics_service import AnalyticsService
print('Analytics service fixed successfully')
"
```

### 5. Restart Application (Required after Analytics Fix)
```bash
docker-compose restart web
```

### 6. Verify Analytics System (Optional)
```bash
docker exec -it salon-ese-web-1 python test_analytics_system.py
```

## What's Updated

### Phase 3 - Commission Calculation System (v2.4.0)
- **Enhanced Database Models**: Added commission tracking fields to `AppointmentCost`
- **Billing Elements**: 5 default billing elements (Color, Electric, Styling, Treatment, Other)
- **Commission Calculations**: Advanced commission breakdown with billing element integration
- **Performance Analytics**: Commission efficiency metrics and stylist rankings
- **Admin Interfaces**: Commission reports, stylist performance tracking, billing element management

### Phase 4 - Advanced Analytics System (v2.5.0)
- **Executive Dashboard**: High-level KPIs and comprehensive metrics overview
- **Holiday Analytics**: Trend analysis, conflict detection, and approval rate tracking
- **Commission Analytics**: Performance rankings, monthly trends, and billing element analysis
- **Staff Utilization Analytics**: Capacity planning, utilization rates, and productivity metrics
- **Date Range Filtering**: Flexible reporting periods for all analytics
- **Capacity Recommendations**: Automated planning suggestions for optimal staffing

### New Admin Features Added:
- **Commission Reports**: `/admin/commission/reports`
- **Stylist Performance**: `/admin/commission/stylist-performance/<id>`
- **Salon Commission Summary**: `/admin/commission/salon-summary`
- **Billing Elements Management**: `/admin/commission/billing-elements`
- **Executive Analytics Dashboard**: `/admin/analytics/dashboard`
- **Holiday Trends Analytics**: `/admin/analytics/holiday-trends`
- **Commission Trends Analytics**: `/admin/analytics/commission-trends`
- **Staff Utilization Analytics**: `/admin/analytics/staff-utilization`

### New Service Layer:
- **Enhanced HRService**: Advanced commission calculations with billing elements
- **AnalyticsService**: Comprehensive analytics for all business metrics
- **Executive Dashboard Data**: KPI calculations and trend analysis
- **Capacity Planning**: Automated recommendations and utilization tracking

### Analytics Features:
- **Financial KPIs**: Revenue, commission, and efficiency metrics
- **Staff Metrics**: Utilization rates, productivity, and performance tracking
- **Holiday Management**: Request trends, approval rates, and conflict detection
- **Capacity Planning**: Automated recommendations for optimal staffing
- **Performance Rankings**: Stylist performance comparisons and rankings
- **Trend Analysis**: Monthly and quarterly trend analysis across all metrics
- **Real-time Updates**: Live data refresh and dynamic filtering

## System Status
After running these commands, the system will be updated to version v2.5.0 with:
- Complete Commission Calculation System
- Advanced Analytics System with Executive Dashboard
- Enhanced HR and Financial Tracking
- Comprehensive Reporting and Analytics

## Navigation
- **Commission Reports**: Accessible from "Admin Panel" → "Commission Reports"
- **Analytics Dashboard**: Accessible from "Admin Panel" → "Analytics Dashboard"
- **Billing Elements**: Accessible from Commission Reports → "Billing Elements"

## Troubleshooting

### If Commission Migration Fails
```bash
# Check if columns already exist
docker exec -it salon-ese-web-1 python -c "
from app import create_app, db
from sqlalchemy import inspect
app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('appointment_cost')]
    print('AppointmentCost columns:', columns)
"
```

### If Analytics Service Import Fails
```bash
# Check if AnalyticsService exists
docker exec -it salon-ese-web-1 python -c "
import sys
sys.path.append('/app')
from app.services.analytics_service import AnalyticsService
print('AnalyticsService imported successfully')
"
```

### If Database Connection Issues
```bash
# Restart database container
docker-compose restart db

# Wait for database to be ready
docker-compose logs -f db
```

### If Test Data Creation Fails
```bash
# Check if services exist
docker exec -it salon-ese-web-1 python -c "
from app import create_app
from app.models import Service
app = create_app()
with app.app_context():
    services = Service.query.all()
    print(f'Found {len(services)} services')
"
```

## Version History
- **v2.4.0**: Commission Calculation System
- **v2.5.0**: Advanced Analytics System (Current)

---

## 🆕 NEW: Seniority System Setup (v2.3.0)

### Overview
The latest update adds a comprehensive seniority-based stylist hierarchy system with advanced calendar functionality. This includes role-based color coding, filter persistence, and professional calendar views.

### Setup Instructions

#### Option 1: Fresh Installation with Seniority System
If you want to start completely fresh with the new seniority system:

```bash
# 1. Nuclear reset (if needed)
docker-compose down
docker volume rm salon-ese_postgres_data
docker-compose up -d

# 2. Initialize services
docker exec -it salon-ese-web-1 python init_services.py

# 3. Add seniority roles
docker exec -it salon-ese-web-1 python add_seniority_roles.py

# 4. Create comprehensive test data with seniority hierarchy
docker exec -it salon-ese-web-1 python create_ranked_test_data.py
```

#### Option 2: Update Existing System
If you have an existing system and want to add the seniority system:

```bash
# 1. Add seniority roles to existing system
docker exec -it salon-ese-web-1 python add_seniority_roles.py

# 2. Verify roles were created
docker exec -it salon-ese-web-1 python check_roles.py

# 3. (Optional) Create new test data with seniority hierarchy
docker exec -it salon-ese-web-1 python create_ranked_test_data.py
```

### What the Seniority System Adds

#### New Roles Created:
- **Owner**: Full management access, high salary
- **Manager**: Management capabilities, good salary  
- **Senior Stylist**: High commission (75%), all services, 20% faster timing
- **Stylist**: Medium commission (65%), most services, standard timing
- **Junior Stylist**: Lower commission (50%) or hourly, basic services, 20% slower timing

#### Calendar Enhancements:
- **24-Hour Time Format**: Professional time display
- **Filter Persistence**: Calendar filters maintain state across navigation
- **Horizontal Scrolling**: Week view supports unlimited stylists
- **Color-Coded Headers**: Visual distinction by seniority level
- **Role-Based Filtering**: Filter calendar by specific seniority roles

#### Test Data Features:
- **Realistic Employment**: Different compensation models by seniority
- **Service Access Control**: Stylist service access based on experience
- **Work Pattern Integration**: Seniority-appropriate schedules
- **Holiday Quotas**: Different holiday entitlements by seniority

### New Test Login Credentials (Seniority System)
```
Owner: salon_owner / 12345678
Manager: salon_manager / 12345678
Senior Stylists: emma_wilson, james_brown, sophie_davis / 12345678
Regular Stylists: michael_taylor, olivia_anderson, david_martinez, lisa_thompson / 12345678
Junior Stylists: alex_johnson, maya_garcia, ryan_lee / 12345678
Customers: alice_j, bob_smith, carol_w, dan_jones, eve_garcia / 12345678
```

### Verification Commands

#### Check Seniority Roles
```bash
docker exec -it salon-ese-web-1 python check_roles.py
```

#### Verify Test Data Creation
```bash
docker exec -it salon-ese-web-1 python -c "
from app import create_app
from app.models import User, Role, EmploymentDetails, WorkPattern, HolidayQuota
app = create_app()
with app.app_context():
    print('=== Seniority System Verification ===')
    print(f'Total Users: {User.query.count()}')
    print(f'Roles: {[r.name for r in Role.query.all()]}')
    print(f'Employment Details: {EmploymentDetails.query.count()}')
    print(f'Work Patterns: {WorkPattern.query.count()}')
    print(f'Holiday Quotas: {HolidayQuota.query.count()}')
    
    # Check seniority hierarchy
    seniority_roles = ['owner', 'manager', 'senior_stylist', 'stylist', 'junior_stylist']
    for role_name in seniority_roles:
        role = Role.query.filter_by(name=role_name).first()
        if role:
            users = User.query.join(User.roles).filter(User.roles.contains(role)).all()
            print(f'{role_name.title()}: {len(users)} users')
"
```

### Troubleshooting Seniority System

#### If Role Creation Fails
```bash
# Check if roles already exist
docker exec -it salon-ese-web-1 python -c "
from app import create_app
from app.models import Role
app = create_app()
with app.app_context():
    roles = Role.query.all()
    print('Existing roles:', [r.name for r in roles])
"
```

#### If Test Data Creation Fails
```bash
# Check for specific errors
docker exec -it salon-ese-web-1 python create_ranked_test_data.py 2>&1 | head -20
```

#### If Calendar View Issues
```bash
# Restart application after seniority system setup
docker-compose restart web
```

### New Features Available
- **Advanced Calendar**: Professional calendar with seniority-based color coding
- **Role-Based Filtering**: Filter appointments by seniority level
- **Filter Persistence**: Calendar filters maintain state across navigation
- **Compact Layout**: Optimized spacing for better information density
- **Responsive Design**: Works on all screen sizes and stylist counts 