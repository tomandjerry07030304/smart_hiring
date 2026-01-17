# Admin Guide - Smart Hiring System

## Table of Contents

1. [System Administration](#system-administration)
2. [Installation & Setup](#installation--setup)
3. [Configuration Management](#configuration-management)
4. [User Management](#user-management)
5. [Database Administration](#database-administration)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Security Management](#security-management)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)
10. [Performance Optimization](#performance-optimization)

---

## System Administration

### Admin Responsibilities

As a system administrator, you are responsible for:

- **System Configuration**: Managing application settings and integrations
- **User Management**: Creating accounts, assigning roles, managing permissions
- **Data Management**: Database maintenance, backups, data integrity
- **Security**: Access control, audit logs, security policies
- **Monitoring**: System health, performance metrics, error tracking
- **Support**: Assisting users, troubleshooting issues

### Admin Access

#### First-Time Setup

After installation, create the admin account:

```powershell
cd scripts
python init_db.py
```

Default admin credentials:
- **Username**: `admin@company.com`
- **Password**: `Admin@123!` (⚠️ Change immediately!)

#### Changing Admin Password

1. Log in as admin
2. Go to **Settings** → **Security** → **Change Password**
3. Use a strong password (12+ characters, mixed case, numbers, symbols)

---

## Installation & Setup

### System Requirements

#### Production Server

**Minimum**:
- Windows Server 2019+ or Ubuntu 20.04+
- 4 CPU cores
- 8 GB RAM
- 50 GB disk space (SSD recommended)
- Internet connection (for MongoDB Atlas)

**Recommended**:
- 8 CPU cores
- 16 GB RAM
- 100 GB SSD
- Dedicated MongoDB server

#### Software Requirements

- **Python**: 3.11+
- **MongoDB**: 5.0+ (local) or Atlas (cloud)
- **Node.js**: 18+ (for development)
- **Web Browser**: Chrome 90+, Firefox 88+, Edge 90+

### Installation Options

#### Option 1: Desktop Application (Recommended for Small Teams)

1. Download `Smart Hiring System-Setup-1.0.0.exe`
2. Run installer as Administrator
3. Follow setup wizard
4. Configure MongoDB connection
5. Create admin account

**Pros**: Easy setup, bundled dependencies, auto-updates  
**Cons**: Single-user or small team only

#### Option 2: Server Deployment with Docker (Recommended for Enterprise)

```bash
# Clone repository
git clone https://github.com/your-org/smart-hiring-system.git
cd smart-hiring-system

# Configure environment
cp .env.template .env
nano .env  # Edit configuration

# Start services
docker-compose -f deploy/docker-compose.yml up -d

# Initialize database
docker exec smart-hiring-backend python scripts/init_db.py
```

**Pros**: Scalable, easy updates, isolated environment  
**Cons**: Requires Docker knowledge

#### Option 3: Manual Installation (Advanced)

```bash
# Install Python dependencies
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate.ps1  # Windows
pip install -r backend/requirements.txt

# Install MongoDB
# See: https://docs.mongodb.com/manual/installation/

# Configure application
cp .env.template .env
nano .env

# Initialize database
python scripts/init_db.py

# Start application
cd backend
python app.py
```

**Pros**: Full control, customization  
**Cons**: Complex setup, manual updates

---

## Configuration Management

### Environment Variables

Configuration is stored in `.env` file (desktop) or environment variables (server).

#### Critical Settings

```ini
# Application
APP_NAME=Smart Hiring System
APP_ENV=production
PORT=8000

# Database (CRITICAL)
MONGODB_URI=mongodb://localhost:27017/smart_hiring
# Or MongoDB Atlas:
# MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/smart_hiring

# Security (CRITICAL - Change these!)
SECRET_KEY=your-super-secret-key-here-change-this
JWT_SECRET=another-secret-key-for-jwt-tokens

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@company.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@company.com
```

#### File Upload Settings

```ini
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=pdf,doc,docx,txt
UPLOAD_FOLDER=uploads
```

#### Feature Flags

```ini
ENABLE_ANONYMIZATION=true
ENABLE_ML_MATCHING=true
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_AUDIT_LOGS=true
```

### Configuration Best Practices

1. **Never commit secrets** to version control
2. **Use strong, unique keys** for SECRET_KEY and JWT_SECRET
3. **Restrict file uploads** to necessary types only
4. **Enable all security features** in production
5. **Use environment-specific configs** (dev, staging, prod)

### Updating Configuration

#### Desktop Application
1. Navigate to: `%APPDATA%\smart-hiring-system\.env`
2. Edit file with text editor
3. Restart application

#### Docker Deployment
1. Edit `.env` file in project root
2. Restart services:
   ```bash
   docker-compose restart
   ```

#### Manual Installation
1. Edit `.env` in project root
2. Restart backend:
   ```bash
   # Stop: Ctrl+C
   python backend/app.py
   ```

---

## User Management

### User Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Admin** | Full system access | System administrators |
| **Recruiter** | Manage jobs, candidates, assessments | HR team |
| **Hiring Manager** | View candidates, approve hires | Department managers |
| **Candidate** | View applications, upload resumes | Job applicants |

### Creating Users

#### Via Admin Dashboard

1. Log in as admin
2. Go to **Users** → **Add User**
3. Fill in details:
   - Name
   - Email
   - Role
   - Initial password (user changes on first login)
4. Click **Create User**
5. Send credentials securely to user

#### Via Database Script

```python
# scripts/create_user.py
from backend.models import User
from werkzeug.security import generate_password_hash

user = User(
    email="recruiter@company.com",
    password=generate_password_hash("TempPass123!"),
    name="Jane Recruiter",
    role="recruiter",
    is_active=True
)
user.save()
```

### Managing Users

#### Deactivating Users

1. **Users** → Find user → **Actions** → **Deactivate**
2. User can no longer log in
3. Data is preserved for audit purposes

#### Resetting Passwords

1. **Users** → Find user → **Actions** → **Reset Password**
2. Generate temporary password
3. Send securely to user
4. User must change on next login

#### Changing Roles

1. **Users** → Find user → **Edit**
2. Change **Role** dropdown
3. Save changes
4. User's permissions update immediately

### Bulk User Import

For large organizations:

```python
# scripts/bulk_import_users.py
import csv
from backend.models import User

with open('users.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        user = User(
            email=row['email'],
            name=row['name'],
            role=row['role'],
            password=generate_password_hash(row['temp_password'])
        )
        user.save()
```

CSV format:
```csv
email,name,role,temp_password
john@company.com,John Doe,recruiter,TempPass1!
jane@company.com,Jane Smith,hiring_manager,TempPass2!
```

---

## Database Administration

### MongoDB Management

#### Connection Strings

**Local MongoDB**:
```
mongodb://localhost:27017/smart_hiring
```

**MongoDB Atlas (Cloud)**:
```
mongodb+srv://username:password@cluster.mongodb.net/smart_hiring
```

**Replica Set (Production)**:
```
mongodb://mongo1:27017,mongo2:27017,mongo3:27017/smart_hiring?replicaSet=rs0
```

### Collections

| Collection | Purpose | Indexes |
|------------|---------|---------|
| `users` | User accounts | email (unique) |
| `jobs` | Job postings | status, created_at |
| `candidates` | Candidate profiles | email, job_id |
| `resumes` | Resume files | candidate_id |
| `assessments` | Skill assessments | candidate_id |
| `matches` | Job-candidate matches | job_id, score |
| `audit_logs` | Activity logs | timestamp, user_id |
| `settings` | System settings | key (unique) |

### Database Initialization

```bash
python scripts/init_db.py
```

This creates:
- Collections with proper schemas
- Indexes for performance
- Default admin user
- Initial settings

### Database Maintenance

#### View Statistics

```bash
mongo smart_hiring --eval "db.stats()"
```

#### Check Indexes

```bash
mongo smart_hiring --eval "db.users.getIndexes()"
```

#### Rebuild Indexes

```bash
mongo smart_hiring --eval "db.users.reIndex()"
```

#### Compact Database

```bash
mongo smart_hiring --eval "db.runCommand({compact: 'users'})"
```

### Performance Monitoring

```javascript
// Enable profiling
db.setProfilingLevel(1, { slowms: 100 })

// View slow queries
db.system.profile.find().sort({ts: -1}).limit(10)
```

---

## Monitoring & Maintenance

### Health Checks

#### Application Health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T10:30:00Z",
  "database": "connected",
  "version": "1.0.0"
}
```

#### Database Health

```bash
mongo --eval "db.adminCommand('ping')"
```

### Log Files

#### Desktop Application

**Location**: `%APPDATA%\smart-hiring-system\logs\`

Files:
- `main.log` - Application events
- `backend.log` - Backend API logs
- `error.log` - Errors only

#### Server Deployment

**Location**: `logs/` directory

Files:
- `app.log` - Main application log
- `access.log` - API access log
- `error.log` - Error log

#### Log Rotation

Logs automatically rotate:
- Daily rotation
- Keep 30 days
- Compress old logs

Manual rotation:
```bash
python scripts/rotate_logs.py
```

### Monitoring Metrics

#### System Metrics
- CPU usage
- Memory usage
- Disk space
- Network I/O

#### Application Metrics
- Active users
- Request rate
- Response time
- Error rate

#### Business Metrics
- Jobs posted
- Applications received
- Matches made
- Hires completed

### Scheduled Maintenance

#### Daily Tasks
- [ ] Review error logs
- [ ] Check system health
- [ ] Monitor disk space

#### Weekly Tasks
- [ ] Database backup
- [ ] Review performance metrics
- [ ] Update documentation

#### Monthly Tasks
- [ ] Security audit
- [ ] Update dependencies
- [ ] Capacity planning

---

## Security Management

### Access Control

#### Password Policy

Enforce strong passwords:
- Minimum 12 characters
- Mixed case required
- Numbers required
- Special characters required
- No common passwords
- Password expiry: 90 days (configurable)

#### Session Management

- Session timeout: 30 minutes inactivity
- Maximum session: 8 hours
- Single session per user (configurable)

### Audit Logging

All admin actions are logged:
- User creation/deletion
- Role changes
- Configuration changes
- Data exports
- Login attempts (failed and successful)

View audit logs:
1. **Admin** → **Audit Logs**
2. Filter by date, user, action
3. Export to CSV for compliance

### Security Best Practices

1. **Keep Software Updated**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Use HTTPS** in production
3. **Enable firewall** (only allow ports 80, 443, 27017)
4. **Regular security audits**
5. **Principle of least privilege**
6. **Multi-factor authentication** (coming soon)

---

## Backup & Recovery

### Backup Strategy

#### Automated Daily Backups

```bash
#!/bin/bash
# scripts/backup.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/smart-hiring"

# Backup MongoDB
mongodump --uri="mongodb://localhost:27017/smart_hiring" \
  --out="$BACKUP_DIR/db_$TIMESTAMP"

# Backup uploads
tar -czf "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" uploads/

# Backup configuration
cp .env "$BACKUP_DIR/config_$TIMESTAMP.env"

# Keep only last 30 days
find "$BACKUP_DIR" -mtime +30 -delete
```

#### Manual Backup

```bash
python scripts/backup_db.py --output=backup.archive
```

### Restore Procedures

#### Restore Database

```bash
mongorestore --uri="mongodb://localhost:27017/smart_hiring" \
  --drop backup_dir/
```

#### Restore Files

```bash
tar -xzf uploads_backup.tar.gz -C /
```

### Disaster Recovery

1. **Install fresh application**
2. **Restore database** from backup
3. **Restore uploaded files**
4. **Restore configuration**
5. **Test system thoroughly**
6. **Notify users**

---

## Troubleshooting

### Common Issues

#### Application Won't Start

**Symptoms**: Error on startup, blank screen

**Solutions**:
1. Check MongoDB is running
2. Verify `.env` configuration
3. Check port 8000 is available
4. Review logs for errors

#### Database Connection Failed

**Symptoms**: "Cannot connect to database"

**Solutions**:
1. Verify `MONGODB_URI` in `.env`
2. Check MongoDB is running: `systemctl status mongod`
3. Test connection: `mongo smart_hiring`
4. Check network/firewall

#### Slow Performance

**Symptoms**: Long load times, timeouts

**Solutions**:
1. Check database indexes
2. Review slow query log
3. Increase server resources
4. Optimize queries
5. Add caching

#### Out of Disk Space

**Symptoms**: "No space left on device"

**Solutions**:
1. Clean old logs: `find logs/ -mtime +30 -delete`
2. Archive old uploads
3. Clean temp files
4. Expand disk space

### Getting Help

1. **Check documentation** (this guide)
2. **Review logs** for error messages
3. **Search GitHub issues**
4. **Contact support**: support@smarthiring.com

---

## Performance Optimization

### Database Optimization

```javascript
// Create indexes
db.candidates.createIndex({job_id: 1, score: -1})
db.jobs.createIndex({status: 1, created_at: -1})
db.audit_logs.createIndex({timestamp: -1}, {expireAfterSeconds: 7776000})

// Analyze query performance
db.candidates.find({job_id: "123"}).explain("executionStats")
```

### Caching

Enable Redis caching (optional):
```ini
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_TTL=3600
```

### File Storage Optimization

Use cloud storage for large files:
```ini
STORAGE_TYPE=s3
AWS_BUCKET=smart-hiring-uploads
AWS_REGION=us-east-1
```

### Scaling

For high traffic:
1. **Load Balancer** (nginx, HAProxy)
2. **Multiple Backend Instances**
3. **MongoDB Replica Set**
4. **CDN** for static files

---

## Appendix

### Configuration Reference

See `.env.template` for complete configuration options.

### API Endpoints

See `docs/API_DOCUMENTATION.md` for API reference.

### Support Contacts

- **Technical Support**: support@smarthiring.com
- **Security Issues**: security@smarthiring.com
- **Sales/Licensing**: sales@smarthiring.com

---

**Document Version**: 1.0.0  
**Last Updated**: November 14, 2025  
**Maintained By**: Smart Hiring System Team
