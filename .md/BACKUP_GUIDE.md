# Database Backup & Recovery Guide

## 📦 Automated Backups (MongoDB Atlas)

### Configuration

MongoDB Atlas provides automated backups by default:

1. **Continuous Backups** (M10+ clusters)
   - Point-in-time recovery
   - Retain snapshots for 2+ days
   - Restore to any point within retention window

2. **Cloud Backups** (All tiers)
   - Daily snapshots
   - Configurable retention (7-365 days)
   - Cross-region backup copies

### Enable Backups

1. Log into MongoDB Atlas
2. Go to your cluster
3. Click "Backup" tab
4. Enable continuous/cloud backups
5. Configure retention policy:
   ```
   Daily: 7 days
   Weekly: 4 weeks
   Monthly: 12 months
   ```

## 🔄 Manual Backup Process

### Using mongodump

```powershell
# Full database backup
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/smart_hiring" --out="./backup-$(Get-Date -Format 'yyyy-MM-dd')"

# Specific collections
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/smart_hiring" \
  --collection=users \
  --collection=applications \
  --out="./backup-critical-$(Get-Date -Format 'yyyy-MM-dd')"

# Compressed backup
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/smart_hiring" \
  --archive="./backup-$(Get-Date -Format 'yyyy-MM-dd').gz" \
  --gzip
```

### Using Atlas Data Export

1. Go to Atlas dashboard
2. Navigate to cluster
3. Click "..." → "Export Data"
4. Select collections
5. Download as JSON or BSON

## 📥 Restore Process

### From mongodump

```powershell
# Restore full database
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net/smart_hiring" ./backup-2025-11-30

# Restore specific collection
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net/smart_hiring" \
  --collection=users \
  ./backup-2025-11-30/smart_hiring/users.bson

# Restore from compressed archive
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net/smart_hiring" \
  --archive="./backup-2025-11-30.gz" \
  --gzip
```

### From Atlas Snapshot

1. Go to cluster → Backups
2. Find desired snapshot
3. Click "Restore"
4. Choose restore option:
   - **Download**: Get files locally
   - **Query**: Browse snapshot data
   - **Restore to cluster**: Overwrite existing
   - **Clone to new cluster**: Safe testing

## 🔍 Backup Verification

### Monthly Verification Checklist

```powershell
# 1. Download latest backup
mongodump --uri="$MONGODB_URI" --out="./verify-backup"

# 2. Restore to test database
$TEST_URI = "mongodb://localhost:27017/test_restore"
mongorestore --uri="$TEST_URI" --drop ./verify-backup

# 3. Verify record counts
python -c "
from pymongo import MongoClient
import os

prod = MongoClient(os.getenv('MONGODB_URI'))
test = MongoClient('mongodb://localhost:27017/test_restore')

prod_db = prod['smart_hiring']
test_db = test['smart_hiring']

collections = ['users', 'jobs', 'applications', 'questions', 'quizzes']

print('Collection Verification:')
for coll in collections:
    prod_count = prod_db[coll].count_documents({})
    test_count = test_db[coll].count_documents({})
    status = '✅' if prod_count == test_count else '❌'
    print(f'{status} {coll}: prod={prod_count}, test={test_count}')
"

# 4. Test critical queries
# 5. Verify data integrity
# 6. Document restore time
```

## 📋 Backup Schedule

### Recommended Schedule

| Frequency | Retention | Storage |
|-----------|-----------|---------|
| **Hourly** (continuous) | 48 hours | Atlas (automated) |
| **Daily** | 7 days | Atlas (automated) |
| **Weekly** | 4 weeks | Atlas + S3/Drive |
| **Monthly** | 12 months | S3/Drive |
| **Yearly** | 7 years | Cold storage |

### Automation Script

```powershell
# backup-scheduler.ps1
$DATE = Get-Date -Format "yyyy-MM-dd"
$BACKUP_DIR = "C:\backups\smart-hiring"
$MONGO_URI = $env:MONGODB_URI

# Create backup directory
New-Item -ItemType Directory -Force -Path "$BACKUP_DIR\$DATE"

# Run backup
mongodump --uri="$MONGO_URI" \
  --archive="$BACKUP_DIR\$DATE\backup.gz" \
  --gzip

# Upload to cloud (example: AWS S3)
aws s3 cp "$BACKUP_DIR\$DATE\backup.gz" \
  "s3://smart-hiring-backups/$DATE/backup.gz"

# Clean old local backups (keep last 7 days)
Get-ChildItem $BACKUP_DIR | 
  Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} |
  Remove-Item -Recurse -Force

Write-Host "✅ Backup completed: $DATE"
```

Schedule with Windows Task Scheduler:
```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-File C:\scripts\backup-scheduler.ps1"

$trigger = New-ScheduledTaskTrigger -Daily -At 2am

Register-ScheduledTask -TaskName "SmartHiring-Backup" `
  -Action $action -Trigger $trigger
```

## 🚨 Disaster Recovery

### RTO & RPO Targets

- **RTO** (Recovery Time Objective): 4 hours
- **RPO** (Recovery Point Objective): 1 hour

### Recovery Scenarios

#### 1. Accidental Data Deletion

```powershell
# Restore specific collection from last night's backup
mongorestore --uri="$MONGODB_URI" \
  --collection=users \
  --drop \
  ./backup-latest/smart_hiring/users.bson
```

#### 2. Database Corruption

```powershell
# Restore from last known good snapshot
# 1. Stop application (prevent writes)
# 2. Restore from Atlas snapshot to new cluster
# 3. Update connection string in app
# 4. Verify data integrity
# 5. Resume application
```

#### 3. Complete Data Center Failure

```powershell
# Atlas handles this automatically with multi-region replication
# Manual steps:
# 1. Verify replica set failover occurred
# 2. Check application connectivity
# 3. Monitor performance
# 4. Document incident
```

## 📊 Monitoring Backups

### Atlas Alerts

Configure alerts in Atlas dashboard:
- Backup failure
- Snapshot missing
- Disk space threshold
- Replication lag

### Verification Script

```python
# check-backups.py
import os
from datetime import datetime, timedelta
import boto3  # If using S3

def verify_backups():
    """Verify backups exist and are recent"""
    
    # Check Atlas snapshots via API
    # Check S3 backup files
    # Verify backup sizes are reasonable
    # Alert if backups are missing or too old
    
    backup_dir = "C:/backups/smart-hiring"
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    backup_file = f"{backup_dir}/{yesterday.strftime('%Y-%m-%d')}/backup.gz"
    
    if os.path.exists(backup_file):
        size_mb = os.path.getsize(backup_file) / (1024 * 1024)
        print(f"✅ Backup verified: {size_mb:.2f} MB")
        return True
    else:
        print(f"❌ Backup missing: {backup_file}")
        # Send alert email/Slack
        return False

if __name__ == '__main__':
    verify_backups()
```

## 📝 Backup Checklist

### Weekly
- [ ] Verify automated backups are running
- [ ] Check backup sizes (should be consistent)
- [ ] Review Atlas backup dashboard
- [ ] Confirm off-site backups uploaded

### Monthly
- [ ] Test restore to dev environment
- [ ] Verify all collections restored correctly
- [ ] Time the restore process (update RTO)
- [ ] Document any issues
- [ ] Update backup documentation

### Quarterly
- [ ] Full disaster recovery drill
- [ ] Review and update retention policies
- [ ] Audit backup access permissions
- [ ] Test cross-region restore
- [ ] Update emergency contacts

## 🔐 Backup Security

### Encryption
- ✅ Atlas encrypts backups at rest (AES-256)
- ✅ Use encrypted connections for transfer
- ✅ Encrypt local backup files

### Access Control
```
Backup Access:
- Database Admin: Full access
- Operations: Read-only
- Developers: No direct access
```

### Compliance
- GDPR: Right to be forgotten impacts backups
- Retention: Comply with data retention policies
- Audit: Log all backup/restore operations

## 📱 Emergency Contacts

| Role | Name | Contact |
|------|------|---------|
| Database Admin | [Name] | [Email/Phone] |
| DevOps Lead | [Name] | [Email/Phone] |
| MongoDB Support | - | support@mongodb.com |
| On-Call | [Rotation] | [PagerDuty/Slack] |

## 🔗 Resources

- MongoDB Atlas Backup: https://docs.atlas.mongodb.com/backup/
- mongodump/restore: https://docs.mongodb.com/database-tools/
- Backup Best Practices: https://docs.mongodb.com/manual/core/backups/

---
**Last Updated**: November 2025  
**Review Schedule**: Quarterly  
**Next Review**: February 2026
