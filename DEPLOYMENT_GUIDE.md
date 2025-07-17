# Salon ESE Deployment Guide

## 🚀 Quick Start - Deploy on Any Machine

This guide provides step-by-step instructions for deploying the Salon ESE booking system on any computer with Docker installed.

---

## 📋 Prerequisites

### **Required Software**
- **Docker Desktop** (version 20.10 or higher)
- **Git** (for cloning the repository)

### **System Requirements**
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: At least 2GB free space
- **Network**: Internet connection for initial setup

### **Optional Software**
- **Docker Compose** (usually included with Docker Desktop)
- **A web browser** (Chrome, Firefox, Safari, Edge)

---

## 🔧 Installation Steps

### **Step 1: Install Docker Desktop**

#### **Windows:**
1. Download Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Run the installer and follow the setup wizard
3. Restart your computer when prompted
4. Start Docker Desktop from the Start menu

#### **macOS:**
1. Download Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Drag Docker.app to Applications folder
3. Start Docker Desktop from Applications
4. Grant necessary permissions when prompted

#### **Linux (Ubuntu/Debian):**
```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (optional, for non-sudo access)
sudo usermod -aG docker $USER
```

### **Step 2: Verify Docker Installation**

Open a terminal/command prompt and run:

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Test Docker installation
docker run hello-world
```

You should see output confirming Docker is working correctly.

---

## 📥 Download and Setup

### **Step 3: Clone the Repository**

```bash
# Clone the salon-ese repository
git clone <your-repository-url>
cd salon-ese

# Verify the files are present
ls -la
```

You should see files like:
- `docker-compose.yml`
- `Dockerfile`
- `requirements.txt`
- `app/` directory
- `README.md`

### **Step 4: Start the Application**

```bash
# Start all containers in detached mode
docker-compose up -d

# Check container status
docker-compose ps
```

You should see output like:
```
Name                    Command               State           Ports
--------------------------------------------------------------------------------
salon-ese_db_1         docker-entrypoint.sh postgres    Up      5432/tcp
salon-ese_web_1        python run.py                    Up      0.0.0.0:5000->5000/tcp
```

### **Step 5: Initialize the Database**

```bash
# Run the migration script to create tables and default data
docker-compose exec web python migrate_new_models.py
```

Expected output:
```
Starting migration for new salon management models...
✓ All tables created successfully
Initializing default salon settings...
✓ Default salon settings created
Initializing default billing elements...
✓ Added billing element: Color (25.00%)
✓ Added billing element: Electric (15.00%)
✓ Added billing element: Products (10.00%)
✓ Added billing element: Equipment (5.00%)
✓ Added billing element: Overheads (20.00%)
✓ Migration completed successfully!

Migration Summary:
- Salon Settings: 1 record(s)
- Billing Elements: 5 record(s)
- Total percentage of billing elements: 75.00%
```

### **Step 6: Test the Installation**

```bash
# Run the test script to verify everything works
docker-compose exec web python test_new_models.py
```

### **Step 7: Access the Application**

Open your web browser and navigate to:
```
http://localhost:5000
```

You should see the Salon ESE homepage.

---

## 🔍 Verification and Troubleshooting

### **Check Application Status**

```bash
# View running containers
docker-compose ps

# Check application logs
docker-compose logs web

# Check database logs
docker-compose logs db
```

### **Common Issues and Solutions**

#### **Issue 1: Port 5000 Already in Use**
```bash
# Check what's using port 5000
netstat -an | grep 5000  # Linux/macOS
netstat -an | findstr 5000  # Windows

# Stop the conflicting service or change the port in docker-compose.yml
```

#### **Issue 2: Container Won't Start**
```bash
# Check detailed logs
docker-compose logs -f web

# Restart containers
docker-compose restart

# Complete reset (removes all data)
docker-compose down -v
docker-compose up -d
```

#### **Issue 3: Database Connection Issues**
```bash
# Check database container
docker-compose logs db

# Restart database
docker-compose restart db

# Wait 30 seconds, then restart web
docker-compose restart web
```

#### **Issue 4: Permission Issues (Linux)**
```bash
# Fix Docker permissions
sudo chmod 666 /var/run/docker.sock

# Or add user to docker group
sudo usermod -aG docker $USER
# Then log out and back in
```

---

## 🛠️ Management Commands

### **Daily Operations**

```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs -f

# Restart the application
docker-compose restart

# Update the application (after git pull)
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### **Database Operations**

```bash
# Access database shell
docker-compose exec db psql -U postgres -d salon_ese

# Backup database
docker-compose exec db pg_dump -U postgres salon_ese > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres -d salon_ese < backup.sql
```

### **Application Maintenance**

```bash
# Run database migrations
docker-compose exec web python migrate_new_models.py

# Test the application
docker-compose exec web python test_new_models.py

# Access application shell
docker-compose exec web python

# View application files
docker-compose exec web ls -la
```

---

## 🔐 Security Considerations

### **Production Deployment**

For production use, consider these security enhancements:

1. **Change Default Passwords**
   - Update database passwords in `docker-compose.yml`
   - Use strong, unique passwords

2. **Use HTTPS**
   - Configure SSL certificates
   - Set up reverse proxy (nginx)

3. **Network Security**
   - Restrict container network access
   - Use Docker secrets for sensitive data

4. **Regular Updates**
   - Keep Docker and images updated
   - Monitor for security patches

### **Environment Variables**

Create a `.env` file for sensitive configuration:

```bash
# .env file
POSTGRES_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key
FLASK_ENV=production
```

---

## 📊 Monitoring and Logs

### **View Application Logs**

```bash
# Real-time logs
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100 web

# Logs with timestamps
docker-compose logs -t web
```

### **System Monitoring**

```bash
# Check container resource usage
docker stats

# Check disk usage
docker system df

# Clean up unused resources
docker system prune
```

---

## 🔄 Updates and Maintenance

### **Updating the Application**

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Run any new migrations
docker-compose exec web python migrate_new_models.py
```

### **Backup and Recovery**

```bash
# Create backup
docker-compose exec db pg_dump -U postgres salon_ese > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker-compose exec -T db psql -U postgres -d salon_ese < backup_file.sql
```

---

## 📞 Support and Troubleshooting

### **Getting Help**

1. **Check the logs first**: `docker-compose logs -f`
2. **Verify Docker installation**: `docker --version`
3. **Check system resources**: `docker stats`
4. **Review this guide** for common solutions

### **Useful Commands for Debugging**

```bash
# Check container health
docker-compose ps

# Inspect container details
docker-compose exec web env

# Check file permissions
docker-compose exec web ls -la

# Test database connection
docker-compose exec web python -c "from app import create_app; app = create_app(); print('App created successfully')"
```

---

## ✅ Success Checklist

After following this guide, you should have:

- [ ] Docker Desktop installed and running
- [ ] Repository cloned locally
- [ ] Containers running (`docker-compose ps` shows both containers as "Up")
- [ ] Migration completed successfully
- [ ] Application accessible at http://localhost:5000
- [ ] Test script passes without errors
- [ ] Admin interface accessible (after creating a user account)

---

## 🎯 Next Steps

Once the system is running:

1. **Create an admin account** through the web interface
2. **Configure salon settings** in the admin panel
3. **Add staff members** and set up work patterns
4. **Configure billing elements** for commission calculations
5. **Test the appointment booking system**

---

*This deployment guide covers the complete setup process for the Salon ESE booking system. For additional support, refer to the main README.md file or contact the development team.* 