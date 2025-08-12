# Salon ESE Migration Guide

This guide provides step-by-step instructions for updating your salon-ese Docker container from an older version to include all recent Service Management Enhancements.

## 🚨 Important Notes

- **Backup your data** before running migrations if you have important data
- **Stop the application** before running migrations
- **Test thoroughly** after migration to ensure everything works correctly

## 📋 Pre-Migration Checklist

1. **Check current container status:**
   ```bash
   docker ps
   ```

2. **Note your current data** (if any) that you want to preserve
3. **Ensure you have the latest code** from the repository

## 🔄 Migration Steps

### Step 1: Stop the Current Container

```bash
# Navigate to your salon-ese directory
cd /path/to/salon-ese

# Stop the current containers
docker-compose down
```

### Step 2: Backup Database (Optional but Recommended)

If you have important data you want to preserve:

```bash
# Create a backup of your database
docker exec salon-ese-db-1 pg_dump -U postgres salon_ese > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Step 3: Update Code

Ensure you have the latest code with all the new features:

```bash
# Pull latest changes from repository
git pull origin main

# Or if you're working with a local copy, ensure all new files are present:
# - migrate_stylist_timings.py
# - Updated models.py, forms.py, routes/appointments.py
# - New templates in app/templates/appointments/
```

### Step 4: Rebuild Container with Latest Code

```bash
# Rebuild the container with no cache to ensure all changes are applied
docker-compose build --no-cache

# Start the containers
docker-compose up -d
```

### Step 5: Run Database Migrations

Wait for the containers to be fully started, then run the migration scripts in order:

```bash
# 1. Run the HR system migration (NEW)
docker exec -it salon-ese-web-1 python migrate_hr_system.py

# 2. Run the multi-service appointment migration (if not already done)
docker exec -it salon-ese-web-1 python migrate_appointments_multiservice.py

# 3. Run the stylist timings migration
docker exec -it salon-ese-web-1 python migrate_stylist_timings.py

# 4. Run the stylist-service associations migration
docker exec -it salon-ese-web-1 python migrate_stylist_service_associations.py

# 5. Run the stylist timing waiting time migration
docker exec -it salon-ese-web-1 python migrate_stylist_timing_waiting_time.py
```

### Step 6: Verify Migration Success

Check that all migrations completed successfully. You should see output like:

```
✓ StylistServiceTiming table created
✓ waiting_time column added to Service table
✓ StylistServiceAssociation table created
✓ custom_waiting_time column added to StylistServiceTiming table
✓ Migration completed successfully!
```

**Note:** Each migration script will show its own success messages. If any migration fails, check the error message and ensure the previous migrations completed successfully before retrying.

### Step 7: Test the Application

1. **Access the application** at `http://localhost:5010`
2. **Log in** with your existing credentials
3. **Navigate to "Stylist Timings"** in the menu (for managers/owners)
4. **Navigate to "Stylist Associations"** in the menu (for managers/owners)
5. **Check "Services"** page to see waiting time fields
6. **Test booking an appointment** with the new features
7. **Verify custom waiting times** work in stylist timing forms

## 🐛 Troubleshooting

### Migration Fails with "Table Already Exists"

If you see errors about tables already existing:

```bash
# Check what tables exist
docker exec -it salon-ese-web-1 python -c "
from app import create_app
from app.extensions import db
from sqlalchemy import inspect
app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    print('Existing tables:', inspector.get_table_names())
"
```

### Container Won't Start

If the container fails to start:

```bash
# Check container logs
docker-compose logs -f

# Check for port conflicts
docker ps

# Restart with fresh build
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues

If you can't connect to the database:

```bash
# Check database container status
docker ps | grep salon-ese-db

# Check database logs
docker logs salon-ese-db-1

# Restart database container
docker-compose restart db
```

## 🗑️ Nuclear Option: Complete Database Reset

**⚠️ WARNING: This will completely delete all data in your database!**

If migrations fail repeatedly or you encounter persistent database issues, you can perform a complete database reset. This is especially useful for fresh installations or when you don't need to preserve existing data.

---

### Step 1: Stop All Containers
Stop the application and database containers.
```bash
# In your salon-ese project directory:
docker-compose down
```

---

### Step 2: Remove the Database Volume
This deletes ALL data in the PostgreSQL database.
```bash
# Remove the database volume (named 'salon-ese_postgres_data'):
docker volume rm salon-ese_postgres_data

# (Optional) Verify the volume is gone:
docker volume ls | grep salon-ese
```

---

### Step 3: Clean Up Docker Resources (Optional)
Remove stopped containers, unused images, and unused volumes. Only do this if you are sure you don't need them for other projects.
```bash
# Remove stopped containers:
docker container prune -f

# Remove unused images:
docker image prune -f

# Remove unused volumes:
docker volume prune -f
```

---

### Step 4: Rebuild and Start Fresh Containers
Build everything from scratch and start the containers.
```bash
# Rebuild containers with no cache:
docker-compose build --no-cache

# Start containers in the background:
docker-compose up -d
```

---

### Step 5: Wait for Database Initialization
Wait for the database to be ready before proceeding.
```bash
# Watch the database logs until you see:
# "database system is ready to accept connections"
docker-compose logs -f db
```

---

### Step 6: Run Database Migrations
Run the migration scripts to create all tables with the correct schema:
```bash
# Run each migration in order (these will create tables with the correct schema):
docker exec -it salon-ese-web-1 python migrate_appointments_multiservice.py
docker exec -it salon-ese-web-1 python migrate_stylist_timings.py
docker exec -it salon-ese-web-1 python migrate_stylist_service_associations.py
docker exec -it salon-ese-web-1 python migrate_stylist_timing_waiting_time.py
```

**Note:** The migration scripts will create all necessary tables with the correct schema, including the `booked_by_id` and `waiting_time` columns.

---

### Step 7: Add Sample Data
Populate the database with sample services and test users.
```bash
# Add sample services:
docker exec -it salon-ese-web-1 python init_services.py

# (Optional) Add test users:
docker exec -it salon-ese-web-1 python add_test_users.py
```

---

### Step 8: Verify Fresh Installation
1. Open your browser and go to: http://localhost:5010
2. Log in with test credentials:
   - Manager: `manager_1` / `12345678`
   - Stylist: `stylist_1` / `12345678`
   - Customer: `cust_1` / `12345678`
3. Check that the app works as expected.

---

### Troubleshooting Nuclear Reset

#### Database Won't Start
```bash
# Check if port 5432 is in use:
netstat -an | grep 5432

# (Linux/Mac) Kill any process using port 5432:
sudo lsof -ti:5432 | xargs kill -9

# Restart containers:
docker-compose down
docker-compose up -d
```

#### Permission Issues
```bash
# (Linux/Mac) Fix volume permissions:
sudo chown -R 999:999 /var/lib/docker/volumes/salon-ese_postgres_data

# (Windows) Run Docker Desktop as Administrator
```

#### Container Health Check Fails
```bash
# Check database logs for errors:
docker-compose logs db

# Manually test DB connection:
docker exec -it salon-ese-db-1 psql -U salon_user -d salon_ese -c "SELECT 1;"
```

---

### When to Use Nuclear Reset
- ✅ Fresh install or development
- ✅ Migrations fail repeatedly
- ✅ No data to preserve
- ❌ Not for production or if you need to keep data

---

### Alternative: Selective Table Reset
If you only want to drop specific tables:
```bash
# Connect to the database:
docker exec -it salon-ese-db-1 psql -U salon_user -d salon_ese

# Drop a table (replace table_name):
DROP TABLE IF EXISTS table_name CASCADE;

# Exit psql:
\q

# Rerun the relevant migration script:
docker exec -it salon-ese-web-1 python migrate_specific_table.py
```

## 📊 Post-Migration Verification

After successful migration, verify these features work:

### ✅ HR System Integration
- [ ] "HR Dashboard" link appears in navigation (managers/owners)
- [ ] Employment details form includes new HR fields (start_date, end_date, rates)
- [ ] Can create employment details with different employment types
- [ ] Form validation works for employment-specific fields
- [ ] Date validation works for employment periods

### ✅ Appointment Cost Tracking
- [ ] Appointment costs are calculated automatically when appointments are booked
- [ ] Cost breakdowns show in appointment view (Service Revenue, Stylist Cost, Salon Profit)
- [ ] Appointment costs page displays detailed breakdowns with filtering
- [ ] Profit margin calculations are accurate
- [ ] Calculation methods (hourly vs commission) work correctly

### ✅ HR Dashboard & Reports
- [ ] HR Dashboard displays financial summary cards correctly
- [ ] Employment summary shows stylist counts and employment types
- [ ] Filtering by date range and stylist works
- [ ] Stylist earnings reports display with rankings
- [ ] Date range filtering works in all reports

### ✅ Service Management
- [ ] Can add/edit services with waiting times
- [ ] Services page shows waiting time information
- [ ] Service form includes waiting time field

### ✅ Stylist Timing Management
- [ ] "Stylist Timings" link appears in navigation (managers/owners)
- [ ] Can add new stylist timing entries with custom waiting times
- [ ] Can edit existing stylist timings
- [ ] Stylist timings list shows time savings and custom waiting times
- [ ] Custom waiting time field auto-populates with service defaults

### ✅ Stylist Service Associations
- [ ] "Stylist Associations" link appears in navigation (managers/owners)
- [ ] Can add new stylist-service associations
- [ ] Can edit existing associations
- [ ] Booking form filters services based on stylist permissions
- [ ] API endpoint returns stylist-allowed services

### ✅ Appointment Booking
- [ ] Booking form includes stylist timing checkbox
- [ ] Can add multiple services to appointments
- [ ] Waiting times are included in duration calculations
- [ ] Stylist timing is used when checkbox is selected
- [ ] Custom waiting times are applied when stylist timing is enabled
- [ ] Service selection is filtered based on stylist permissions

### ✅ Multi-Service Appointments
- [ ] Appointments can have multiple services
- [ ] Calendar displays multi-service appointments correctly
- [ ] Appointment details show all services

## 🔧 Rollback Instructions

If you need to rollback to the previous version:

```bash
# Stop current containers
docker-compose down

# Restore from backup (if you created one)
docker exec -i salon-ese-db-1 psql -U postgres salon_ese < backup_YYYYMMDD_HHMMSS.sql

# Rebuild with previous code version
git checkout <previous-commit-hash>
docker-compose build --no-cache
docker-compose up -d
```

## 📞 Support

If you encounter issues during migration:

1. **Check the troubleshooting section** above
2. **Review container logs** for specific error messages
3. **Ensure all files are present** in your codebase
4. **Verify database connectivity** and permissions

## 🎯 What's New

This migration adds the following major features:

### **v2.0.0 Features:**
- **HR System Integration** with employment details and cost calculations
- **Enhanced Employment Details** with start/end dates and pay rates
- **Appointment Cost Tracking** with automatic cost calculations
- **HR Dashboard** with financial overview and reporting
- **Stylist Earnings Reports** with date range filtering
- **Business Logic Layer** with HRService for calculations

### **v1.2.0 Features:**
- **Stylist-service associations** to control which stylists can perform which services
- **Custom waiting times** for individual stylist-service combinations
- **Dynamic service filtering** in booking forms based on stylist permissions
- **API endpoints** for stylist-service data
- **Enhanced booking experience** with permission-based service selection

### **v1.1.0 Features:**
- **Service waiting times** for color processing and other services
- **Stylist-specific service durations** for faster/slower stylists
- **Enhanced appointment booking** with timing options
- **Multi-service appointment support** (already implemented)
- **Improved service management** interface
- **Stylist timing management** system

### **Migration Scripts Included:**
1. `migrate_hr_system.py` - HR system integration with employment details and cost tracking
2. `migrate_appointments_multiservice.py` - Multi-service appointment support
3. `migrate_stylist_timings.py` - Stylist timing and service waiting time features
4. `migrate_stylist_service_associations.py` - Stylist-service permission system
5. `migrate_stylist_timing_waiting_time.py` - Custom waiting time for stylist timings

For detailed information about the new features, see the updated project documentation. 