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
# 1. Run the multi-service appointment migration (if not already done)
docker exec -it salon-ese-web-1 python migrate_appointments_multiservice.py

# 2. Run the stylist timings migration
docker exec -it salon-ese-web-1 python migrate_stylist_timings.py

# 3. Run the stylist-service associations migration
docker exec -it salon-ese-web-1 python migrate_stylist_service_associations.py

# 4. Run the stylist timing waiting time migration
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

## 📊 Post-Migration Verification

After successful migration, verify these features work:

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

### **v1.1.0 Features:**
- **Service waiting times** for color processing and other services
- **Stylist-specific service durations** for faster/slower stylists
- **Enhanced appointment booking** with timing options
- **Multi-service appointment support** (already implemented)
- **Improved service management** interface
- **Stylist timing management** system

### **v1.2.0 Features:**
- **Stylist-service associations** to control which stylists can perform which services
- **Custom waiting times** for individual stylist-service combinations
- **Dynamic service filtering** in booking forms based on stylist permissions
- **API endpoints** for stylist-service data
- **Enhanced booking experience** with permission-based service selection

### **Migration Scripts Included:**
1. `migrate_appointments_multiservice.py` - Multi-service appointment support
2. `migrate_stylist_timings.py` - Stylist timing and service waiting time features
3. `migrate_stylist_service_associations.py` - Stylist-service permission system
4. `migrate_stylist_timing_waiting_time.py` - Custom waiting time for stylist timings

For detailed information about the new features, see the updated project documentation. 