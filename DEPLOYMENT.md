# Salon ESE - Deployment & Operations Guide

## 🎯 **Overview**

This guide provides comprehensive deployment and operational documentation for the Salon ESE project, covering all deployment options, migration procedures, and operational tasks.

## 🚀 **Deployment Options**

### **1. Docker Compose (Recommended for Development/Testing)**

**Prerequisites:**
- Docker and Docker Compose installed
- Git

**Steps:**
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

### **2. Local Development Setup**

**Prerequisites:**
- Python 3.9+
- PostgreSQL or SQLite
- pip

**Steps:**
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

## 🏭 **Production Deployment**

### **Option 1: Docker Production Deployment**

#### **1.1 Single Server Deployment**

**Prerequisites:**
- Ubuntu 20.04+ server
- Docker and Docker Compose
- Domain name (optional)

**Steps:**

1. **Server Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Application Deployment**
   ```bash
   # Clone repository
   git clone https://github.com/Drum998/salon-ese.git
   cd salon-ese
   
   # Create production environment file
   cp .env.example .env
   nano .env
   ```

3. **Environment Configuration**
   ```bash
   # .env file contents
   FLASK_ENV=production
   SECRET_KEY=your-very-secure-secret-key-here
   DATABASE_URL=postgresql://salon_user:secure_password@db:5432/salon_ese
   POSTGRES_PASSWORD=secure_password
   ```

4. **Start Application**
   ```bash
   # Build and start containers
   docker-compose up -d --build
   
   # Check status
   docker-compose ps
   
   # View logs
   docker-compose logs -f web
   ```

#### **1.2 Multi-Server Deployment**

**Load Balancer Setup:**
```bash
# Install Nginx
sudo apt install nginx

# Configure Nginx
sudo nano /etc/nginx/sites-available/salon-ese

# Nginx configuration
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5010;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/salon-ese /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **Option 2: Cloud Deployment**

#### **2.1 AWS Deployment**

**Prerequisites:**
- AWS account
- AWS CLI configured
- Docker installed

**Steps:**

1. **Create ECS Cluster**
   ```bash
   # Create cluster
   aws ecs create-cluster --cluster-name salon-ese
   
   # Create task definition
   aws ecs register-task-definition --cli-input-json file://task-definition.json
   ```

2. **Deploy Application**
   ```bash
   # Create service
   aws ecs create-service \
     --cluster salon-ese \
     --service-name salon-ese-service \
     --task-definition salon-ese:1 \
     --desired-count 2
   ```

#### **2.2 Google Cloud Platform**

**Prerequisites:**
- GCP account
- gcloud CLI configured

**Steps:**

1. **Create Container Registry**
   ```bash
   # Build and push image
   docker build -t gcr.io/your-project/salon-ese .
   docker push gcr.io/your-project/salon-ese
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy salon-ese \
     --image gcr.io/your-project/salon-ese \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## 🔄 **Database Migrations**

### **Migration Overview**

The Salon ESE system includes several migration scripts to update the database schema as new features are added.

### **Migration Scripts**

#### **1. HR System Migration**
```bash
# Run HR system migration
docker exec -it salon-ese-web-1 python migrate_hr_system.py
```

**What this does:**
- Adds new HR fields to employment_details table
- Creates appointment_cost table
- Updates existing records with default values
- Calculates costs for existing appointments

#### **2. Commission System Migration**
```bash
# Run commission system migration
docker exec -it salon-ese-web-1 python migrate_commission_system.py
```

**What this does:**
- Adds commission_breakdown, billing_method, and billing_elements_applied columns to appointment_cost table
- Creates default billing elements (Color, Electric, Styling, Treatment, Other)
- Updates existing appointment costs with billing method and commission breakdown

#### **3. Stylist Timings Migration**
```bash
# Run stylist timings migration
docker exec -it salon-ese-web-1 python migrate_stylist_timings.py
```

**What this does:**
- Creates StylistServiceTiming table
- Adds custom duration and waiting time support
- Migrates existing service timing data

#### **4. Stylist Service Associations Migration**
```bash
# Run stylist service associations migration
docker exec -it salon-ese-web-1 python migrate_stylist_service_associations.py
```

**What this does:**
- Creates StylistServiceAssociation table
- Sets up stylist-service permission system
- Configures default associations

#### **5. Multi-Service Appointments Migration**
```bash
# Run multi-service appointments migration
docker exec -it salon-ese-web-1 python migrate_appointments_multiservice.py
```

**What this does:**
- Creates AppointmentService table
- Migrates existing single-service appointments to multi-service format
- Preserves all existing appointment data

### **Migration Best Practices**

#### **Pre-Migration Checklist**
1. **Backup Database**
   ```bash
   # Create backup
   docker exec salon-ese-db-1 pg_dump -U salon_user salon_ese > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Stop Application**
   ```bash
   # Stop containers
   docker-compose down
   ```

3. **Update Code**
   ```bash
   # Pull latest changes
   git pull origin main
   ```

#### **Migration Process**
1. **Start Containers**
   ```bash
   # Start containers
   docker-compose up -d
   ```

2. **Run Migrations in Order**
   ```bash
   # Run migrations sequentially
   docker exec -it salon-ese-web-1 python migrate_hr_system.py
   docker exec -it salon-ese-web-1 python migrate_commission_system.py
   docker exec -it salon-ese-web-1 python migrate_stylist_timings.py
   docker exec -it salon-ese-web-1 python migrate_stylist_service_associations.py
   docker exec -it salon-ese-web-1 python migrate_appointments_multiservice.py
   ```

3. **Verify Migration Success**
   ```bash
   # Check migration status
   docker exec -it salon-ese-web-1 python -c "
   from app import create_app
   from app.models import EmploymentDetails, AppointmentCost, StylistServiceTiming
   app = create_app()
   with app.app_context():
       print(f'Employment Details: {EmploymentDetails.query.count()}')
       print(f'Appointment Costs: {AppointmentCost.query.count()}')
       print(f'Stylist Timings: {StylistServiceTiming.query.count()}')
   "
   ```

#### **Post-Migration Tasks**
1. **Test Application**
   - Verify all features work correctly
   - Check admin interfaces
   - Test appointment booking
   - Validate HR calculations

2. **Update Test Data (Optional)**
   ```bash
   # Add comprehensive test data
   docker exec -it salon-ese-web-1 python add_test_users.py
   ```

## 🔧 **Environment Configuration**

### **Environment Variables**

#### **Required Variables**
```bash
# Application Configuration
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-here
FLASK_APP=run.py

# Database Configuration
DATABASE_URL=postgresql://salon_user:secure_password@db:5432/salon_ese
POSTGRES_PASSWORD=secure_password

# Docker Configuration
DOCKER_ENV=true
```

#### **Optional Variables**
```bash
# Email Configuration (if using email features)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/app/logs/salon-ese.log

# Security Configuration
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
PERMANENT_SESSION_LIFETIME=3600
```

### **Configuration Files**

#### **Docker Compose Configuration**
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5010:5010"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://salon_user:${POSTGRES_PASSWORD}@db:5432/salon_ese
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=salon_ese
      - POSTGRES_USER=salon_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

#### **Nginx Configuration**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    location / {
        proxy_pass http://localhost:5010;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 **Monitoring & Maintenance**

### **Health Checks**

#### **Application Health Check**
```bash
# Check application status
curl -f http://localhost:5010/health || echo "Application is down"

# Check database connectivity
docker exec -it salon-ese-web-1 python -c "
from app import create_app
from app.extensions import db
app = create_app()
with app.app_context():
    try:
        db.engine.execute('SELECT 1')
        print('Database connection: OK')
    except Exception as e:
        print(f'Database connection: FAILED - {e}')
"
```

#### **Container Health Check**
```bash
# Check container status
docker-compose ps

# Check container logs
docker-compose logs -f web
docker-compose logs -f db

# Check resource usage
docker stats
```

### **Backup Procedures**

#### **Database Backup**
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/salon-ese"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
docker exec salon-ese-db-1 pg_dump -U salon_user salon_ese > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

#### **Application Backup**
```bash
# Backup application files
tar -czf salon-ese-app-$(date +%Y%m%d_%H%M%S).tar.gz \
  --exclude=venv \
  --exclude=__pycache__ \
  --exclude=.git \
  .
```

### **Log Management**

#### **Log Configuration**
```python
# Logging configuration in config.py
import logging
from logging.handlers import RotatingFileHandler
import os

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/salon-ese.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Salon ESE startup')
```

#### **Log Rotation**
```bash
# Log rotation configuration
sudo nano /etc/logrotate.d/salon-ese

# Configuration
/path/to/salon-ese/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        docker-compose restart web
    endscript
}
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Database Connection Issues**
```bash
# Check database status
docker exec -it salon-ese-db-1 pg_isready -U salon_user

# Check database logs
docker-compose logs db

# Reset database (WARNING: This will delete all data)
docker-compose down
docker volume rm salon-ese_postgres_data
docker-compose up -d
```

#### **Application Startup Issues**
```bash
# Check application logs
docker-compose logs web

# Check environment variables
docker exec -it salon-ese-web-1 env | grep -E "(FLASK|DATABASE)"

# Restart application
docker-compose restart web
```

#### **Migration Issues**
```bash
# Check migration status
docker exec -it salon-ese-web-1 python -c "
from app import create_app
from app.extensions import db
app = create_app()
with app.app_context():
    print('Database tables:')
    for table in db.metadata.tables.keys():
        print(f'  - {table}')
"

# Reset migrations (WARNING: This will delete all data)
docker-compose down
docker volume rm salon-ese_postgres_data
docker-compose up -d
# Then run migrations again
```

### **Performance Issues**

#### **Database Performance**
```bash
# Check database performance
docker exec -it salon-ese-db-1 psql -U salon_user -d salon_ese -c "
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;
"
```

#### **Application Performance**
```bash
# Check application performance
docker exec -it salon-ese-web-1 python -c "
import time
from app import create_app
app = create_app()
with app.app_context():
    start = time.time()
    from app.models import User
    users = User.query.all()
    print(f'Query time: {time.time() - start:.3f}s')
    print(f'Users found: {len(users)}')
"
```

## 🔒 **Security Considerations**

### **Production Security Checklist**

- [ ] **Strong Secret Key**: Use a cryptographically secure secret key
- [ ] **HTTPS**: Enable SSL/TLS encryption
- [ ] **Database Security**: Use strong database passwords
- [ ] **Firewall**: Configure firewall rules
- [ ] **Regular Updates**: Keep system and dependencies updated
- [ ] **Backup Security**: Secure backup storage
- [ ] **Access Control**: Implement proper access controls
- [ ] **Monitoring**: Set up security monitoring

### **Security Headers**
```nginx
# Security headers in Nginx
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
```

---

## ⚡ **QUICK UPDATE SECTION**

### **Complete System Update (HR System to Advanced Analytics)**

This section provides the commands needed to update the Salon ESE system from the HR System migration to the current Advanced Analytics System (v2.5.0).

#### **Fresh Installation (Nuclear Reset)**

If you want to start completely fresh with a clean database and comprehensive test data:

##### **1. Nuclear Database Reset**
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

##### **2. Initialize Services (Required First)**
```bash
docker exec -it salon-ese-web-1 python init_services.py
```

##### **3. Apply Commission System Migration**
```bash
docker exec -it salon-ese-web-1 python migrate_commission_system.py
```

##### **4. Add Comprehensive Test Data**
```bash
docker exec -it salon-ese-web-1 python add_test_users.py
```

##### **5. Verify Installation**
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

#### **Update Commands (Run in Order)**

##### **Prerequisites**
- Your system should have completed the HR System migration (`migrate_hr_system.py`)
- Docker containers should be running
- Database should be accessible

##### **0. Get Latest Version from Github**
```bash
git pull origin main
```

##### **1. Apply Commission System Migration**
```bash
docker exec -it salon-ese-web-1 python migrate_commission_system.py
```

**What this does:**
- Adds `commission_breakdown`, `billing_method`, and `billing_elements_applied` columns to `appointment_cost` table
- Creates default billing elements (Color, Electric, Styling, Treatment, Other)
- Updates existing appointment costs with billing method and commission breakdown

##### **2. Restart Application (Required after Commission Migration)**
```bash
docker-compose restart web
```

##### **3. Verify Commission System (Optional)**
```bash
docker exec -it salon-ese-web-1 python test_commission_system.py
```

##### **4. Fix Analytics Service (Critical - Fixes AttributeError)**
```bash
docker exec -it salon-ese-web-1 python -c "
from app.services.analytics_service import AnalyticsService
print('Analytics service fixed successfully')
"
```

##### **5. Add Test Data (Optional but Recommended)**
```bash
# Add comprehensive test data with seniority hierarchy
docker exec -it salon-ese-web-1 python add_test_users.py
```

##### **6. Verify Complete Installation**
```bash
# Run smoke tests to verify everything works
docker exec -it salon-ese-web-1 python comprehensive_test_runner.py --preset smoke
```

#### **Troubleshooting Quick Updates**

##### **If Commission Migration Fails**
```bash
# Check if columns already exist
docker exec -it salon-ese-web-1 python -c "
from app import create_app
from app.models import AppointmentCost
from app.extensions import db
app = create_app()
with app.app_context():
    try:
        result = db.engine.execute('SELECT commission_breakdown FROM appointment_cost LIMIT 1')
        print('Commission columns already exist')
    except Exception as e:
        print(f'Commission columns missing: {e}')
"

# If columns are missing, run migration again
docker exec -it salon-ese-web-1 python migrate_commission_system.py
```

##### **If Analytics Service Still Has Issues**
```bash
# Check analytics service status
docker exec -it salon-ese-web-1 python -c "
from app.services.analytics_service import AnalyticsService
from datetime import datetime, timedelta
app = create_app()
with app.app_context():
    try:
        summary = AnalyticsService.get_financial_summary(
            datetime.now() - timedelta(days=30),
            datetime.now()
        )
        print('Analytics service working correctly')
    except Exception as e:
        print(f'Analytics service error: {e}')
"
```

##### **If Test Data Creation Fails**
```bash
# Check database connectivity
docker exec -it salon-ese-web-1 python -c "
from app import create_app
from app.extensions import db
app = create_app()
with app.app_context():
    try:
        db.engine.execute('SELECT 1')
        print('Database connection: OK')
    except Exception as e:
        print(f'Database connection: FAILED - {e}')
"

# If database is OK, try test data creation again
docker exec -it salon-ese-web-1 python add_test_users.py
```

#### **Post-Update Verification**

##### **1. Check All Systems**
```bash
# Verify all major systems are working
docker exec -it salon-ese-web-1 python -c "
from app import create_app
from app.models import User, Service, EmploymentDetails, Appointment, AppointmentCost
app = create_app()
with app.app_context():
    print('=== System Status ===')
    print(f'Users: {User.query.count()}')
    print(f'Services: {Service.query.count()}')
    print(f'Employment Details: {EmploymentDetails.query.count()}')
    print(f'Appointments: {Appointment.query.count()}')
    print(f'Appointment Costs: {AppointmentCost.query.count()}')
    print('=== Status: OK ===')
"
```

##### **2. Test Key Features**
```bash
# Test HR system
docker exec -it salon-ese-web-1 python test_hr_system.py

# Test commission system
docker exec -it salon-ese-web-1 python test_commission_system.py

# Test analytics system
docker exec -it salon-ese-web-1 python test_analytics_system.py
```

##### **3. Run Full Test Suite**
```bash
# Run all tests to ensure everything works
docker exec -it salon-ese-web-1 python comprehensive_test_runner.py
```

#### **Rollback Procedure (If Needed)**

If something goes wrong and you need to rollback:

##### **1. Stop Application**
```bash
docker-compose down
```

##### **2. Restore Database Backup**
```bash
# If you have a backup from before the update
docker volume rm salon-ese_postgres_data
docker-compose up -d db
# Wait for database to start
docker exec -i salon-ese-db-1 psql -U salon_user -d salon_ese < backup_before_update.sql
```

##### **3. Restart Application**
```bash
docker-compose up -d
```

##### **4. Verify Rollback**
```bash
# Check that system is back to previous state
docker exec -it salon-ese-web-1 python -c "
from app import create_app
from app.models import User, Appointment
app = create_app()
with app.app_context():
    print(f'Users: {User.query.count()}')
    print(f'Appointments: {Appointment.query.count()}')
"
```

This quick update section provides all the commands needed to update your Salon ESE system to the latest version with all features and improvements. 