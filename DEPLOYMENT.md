# Salon ESE - Deployment Guide

This guide covers deployment options for the Salon ESE authentication system, from development to production environments.

## 🚀 Quick Deployment Options

### 1. Docker Compose (Recommended for Development/Testing)

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

### 2. Local Development Setup

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

## 🏭 Production Deployment

### Option 1: Docker Production Deployment

#### 1.1 Single Server Deployment

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
   # Build and start
   docker-compose -f docker-compose.prod.yml up -d --build
   
   # Check status
   docker-compose ps
   docker-compose logs -f
   ```

#### 1.2 Production Docker Compose

Create `docker-compose.prod.yml`:
```yaml
services:
  web:
    build: .
    ports:
      - "5010:5010"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - DOCKER_ENV=true
    volumes:
      - ./instance:/app/instance
      - ./logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - salon-network

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=salon_ese
      - POSTGRES_USER=salon_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    networks:
      - salon-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U salon_user -d salon_ese"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - salon-network

volumes:
  postgres_data:

networks:
  salon-network:
    driver: bridge
```

### Option 2: Traditional Server Deployment

#### 2.1 Ubuntu Server Setup

**Prerequisites:**
- Ubuntu 20.04+ server
- Python 3.9+
- PostgreSQL 13+
- Nginx
- SSL certificate

**Steps:**

1. **System Preparation**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install required packages
   sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx -y
   ```

2. **PostgreSQL Setup**
   ```bash
   # Create database and user
   sudo -u postgres psql
   
   CREATE DATABASE salon_ese;
   CREATE USER salon_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE salon_ese TO salon_user;
   \q
   ```

3. **Application Setup**
   ```bash
   # Create application directory
   sudo mkdir -p /opt/salon-ese
   sudo chown $USER:$USER /opt/salon-ese
   
   # Clone repository
   cd /opt/salon-ese
   git clone https://github.com/Drum998/salon-ese.git .
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install gunicorn
   ```

4. **Environment Configuration**
   ```bash
   # Create environment file
   nano .env
   
   # Add contents:
   FLASK_ENV=production
   SECRET_KEY=your-very-secure-secret-key-here
   DATABASE_URL=postgresql://salon_user:secure_password@localhost:5432/salon_ese
   ```

5. **Gunicorn Service**
   ```bash
   # Create systemd service
   sudo nano /etc/systemd/system/salon-ese.service
   ```

   Service file contents:
   ```ini
   [Unit]
   Description=Salon ESE Web Application
   After=network.target postgresql.service

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/opt/salon-ese
   Environment="PATH=/opt/salon-ese/venv/bin"
   Environment="FLASK_ENV=production"
   Environment="SECRET_KEY=your-secret-key"
   Environment="DATABASE_URL=postgresql://salon_user:secure_password@localhost:5432/salon_ese"
   ExecStart=/opt/salon-ese/venv/bin/gunicorn --workers 3 --bind unix:salon-ese.sock -m 007 run:app

   [Install]
   WantedBy=multi-user.target
   ```

6. **Nginx Configuration**
   ```bash
   # Create Nginx configuration
   sudo nano /etc/nginx/sites-available/salon-ese
   ```

   Nginx configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           include proxy_params;
           proxy_pass http://unix:/opt/salon-ese/salon-ese.sock;
       }

       location /static {
           alias /opt/salon-ese/app/static;
       }
   }
   ```

7. **Enable Services**
   ```bash
   # Enable Nginx site
   sudo ln -s /etc/nginx/sites-available/salon-ese /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   
   # Start application service
   sudo systemctl start salon-ese
   sudo systemctl enable salon-ese
   ```

8. **SSL Certificate**
   ```bash
   # Obtain SSL certificate
   sudo certbot --nginx -d your-domain.com
   ```

## 🔧 Configuration Management

### Environment Variables

**Required Variables:**
```bash
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
```

**Optional Variables:**
```bash
FLASK_DEBUG=0
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Security Configuration

**Production Security Settings:**
```python
# config.py - ProductionConfig
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # File upload security
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
```

## 📊 Monitoring & Logging

### Logging Configuration

**Application Logs:**
```python
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

### Health Checks

**Health Check Endpoint:**
```python
@app.route('/health')
def health_check():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

## 🔄 Backup & Recovery

### Database Backups

**Automated Backup Script:**
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="salon_ese"
DB_USER="salon_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/salon_ese_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/salon_ese_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "salon_ese_*.sql.gz" -mtime +7 -delete
```

**Cron Job Setup:**
```bash
# Add to crontab
0 2 * * * /opt/salon-ese/backup.sh
```

### Recovery Procedures

**Database Recovery:**
```bash
# Stop application
sudo systemctl stop salon-ese

# Restore database
gunzip -c /opt/backups/salon_ese_20240115_020000.sql.gz | psql -U salon_user salon_ese

# Start application
sudo systemctl start salon-ese
```

## 🔒 Security Hardening

### Firewall Configuration

**UFW Setup:**
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow application port (if not using reverse proxy)
sudo ufw allow 5010

# Check status
sudo ufw status
```

### SSL/TLS Configuration

**Nginx SSL Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/salon-ese/salon-ese.sock;
    }
}
```

## 📈 Performance Optimization

### Gunicorn Configuration

**Production Gunicorn Settings:**
```bash
gunicorn --workers 4 --worker-class sync --worker-connections 1000 --max-requests 1000 --max-requests-jitter 50 --timeout 30 --keep-alive 2 --bind unix:salon-ese.sock run:app
```

### Database Optimization

**PostgreSQL Configuration:**
```sql
-- Increase connection limits
ALTER SYSTEM SET max_connections = 200;

-- Optimize memory settings
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();
```

## 🚨 Troubleshooting

### Common Issues

**1. Database Connection Issues:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -U salon_user -d salon_ese -h localhost

# Check logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

**2. Application Startup Issues:**
```bash
# Check application logs
sudo journalctl -u salon-ese -f

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

**3. Permission Issues:**
```bash
# Fix file permissions
sudo chown -R www-data:www-data /opt/salon-ese
sudo chmod -R 755 /opt/salon-ese
```

### Performance Monitoring

**System Monitoring:**
```bash
# Monitor system resources
htop
iotop
nethogs

# Monitor application
sudo systemctl status salon-ese
sudo journalctl -u salon-ese --since "1 hour ago"
```

## 🔄 Updates & Maintenance

### Application Updates

**Update Procedure:**
```bash
# Stop application
sudo systemctl stop salon-ese

# Backup current version
sudo cp -r /opt/salon-ese /opt/salon-ese.backup.$(date +%Y%m%d)

# Pull latest changes
cd /opt/salon-ese
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
flask db upgrade

# Start application
sudo systemctl start salon-ese

# Check status
sudo systemctl status salon-ese
```

### Scheduled Maintenance

**Maintenance Script:**
```bash
#!/bin/bash
# maintenance.sh

echo "Starting scheduled maintenance..."

# Update system packages
sudo apt update && sudo apt upgrade -y

# Restart services
sudo systemctl restart postgresql
sudo systemctl restart salon-ese
sudo systemctl restart nginx

# Clean up old logs
find /opt/salon-ese/logs -name "*.log" -mtime +30 -delete

# Clean up old backups
find /opt/backups -name "*.sql.gz" -mtime +30 -delete

echo "Maintenance completed."
```

---

**For additional deployment support, please refer to the main README.md or create an issue on GitHub.** 