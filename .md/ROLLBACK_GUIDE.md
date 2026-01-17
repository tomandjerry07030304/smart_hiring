# 🆘 Rollback Guide - Smart Hiring System

## Emergency Rollback Procedures

**⚠️ Use this guide when production deployment fails or introduces critical issues.**

---

## 🚨 When to Rollback

Immediate rollback triggers:
- ✅ Error rate > 5% for 5 minutes
- ✅ Critical feature completely broken
- ✅ Security vulnerability discovered
- ✅ Database corruption detected
- ✅ Performance degradation > 50%
- ✅ User data loss or corruption

Minor issues (fix forward instead):
- ❌ Minor UI bugs
- ❌ Non-critical feature issues
- ❌ Performance degradation < 25%
- ❌ Low-traffic feature broken

---

## 📋 Pre-Rollback Checklist

**Before initiating rollback:**
1. [ ] Confirm issue is production-critical
2. [ ] Notify team in #incidents Slack channel
3. [ ] Create incident ticket with details
4. [ ] Take production database snapshot
5. [ ] Document current error state
6. [ ] Identify last known good version

---

## 🔄 Rollback Methods

### Method 1: Git Revert (Preferred - Zero Downtime)

**Use when:** Code issues, no database schema changes

```bash
# 1. Checkout main branch
git checkout main

# 2. Identify the problematic commit
git log --oneline -10

# 3. Revert the commit (creates new commit)
git revert <bad-commit-hash>

# 4. Push to trigger auto-deploy
git push origin main

# Render will automatically deploy the reverted version
# Downtime: ~2-3 minutes for deploy
```

**✅ Advantages:**
- Clean git history
- Auto-triggers Render deployment
- Can be reverted if needed

**❌ Limitations:**
- Only works if no database changes

---

### Method 2: Render Rollback (Fastest)

**Use when:** Emergency, need immediate rollback

**Steps:**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select `smart-hiring-system` service
3. Click **"Deploys"** tab
4. Find last successful deploy
5. Click **"Rollback to this deploy"**
6. Confirm rollback

**Downtime:** ~1-2 minutes

**✅ Advantages:**
- Fastest method (1 click)
- No git changes needed

**❌ Limitations:**
- Limited to last 10 deploys
- Git and Render out of sync temporarily

---

### Method 3: Manual Deployment (Nuclear Option)

**Use when:** Render rollback unavailable, git history complex

```bash
# 1. Checkout known good version
git checkout <good-commit-hash>

# 2. Force push to deploy branch (careful!)
git push origin HEAD:main --force

# 3. Verify deployment in Render
# 4. Create new branch from good state
git checkout -b hotfix/rollback-$(date +%Y%m%d)
git push origin hotfix/rollback-$(date +%Y%m%d)
```

**⚠️ WARNING:** Force push rewrites git history. Use only in emergencies.

---

## 🗄️ Database Rollback

### Scenario A: No Schema Changes (Most Common)

**Action:** No database rollback needed, code rollback sufficient.

```bash
# Verify no schema changes between versions
git diff <good-version> <bad-version> -- backend/models/
```

---

### Scenario B: Schema Changes (Complex)

**Action:** Restore database from backup + rollback code.

#### Step 1: Stop Application (Prevent Writes)
```bash
# In Render Dashboard:
# 1. Go to Service Settings
# 2. Click "Suspend" (temporary)
# Downtime starts here (~5-10 minutes)
```

#### Step 2: Restore Database from Backup

**Option 1: MongoDB Atlas Point-in-Time Restore**
1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Select cluster → **Backup** tab
3. Click **Restore**
4. Choose restore point (before bad deploy)
5. Select **Download** or **Restore to Cluster**
6. If downloading:
   ```bash
   mongorestore --uri="mongodb+srv://..." --archive=backup.archive
   ```

**Option 2: Manual Backup Restore** (if automated backup exists)
```bash
# Download backup from S3/storage
aws s3 cp s3://backups/smart-hiring-$(date -d yesterday +%Y%m%d).gz .

# Restore to MongoDB Atlas
mongorestore --uri="$MONGO_URI" --gzip --archive=smart-hiring-*.gz
```

#### Step 3: Verify Data Integrity
```bash
# Connect to MongoDB
mongosh "$MONGO_URI"

# Check record counts
use smart_hiring
db.users.countDocuments()
db.jobs.countDocuments()
db.applications.countDocuments()

# Verify latest records
db.applications.find().sort({_id: -1}).limit(5)
```

#### Step 4: Rollback Code (Method 1 or 2 above)

#### Step 5: Resume Application
```bash
# In Render Dashboard:
# 1. Go to Service Settings
# 2. Click "Resume"
```

**Total Downtime:** 10-20 minutes

---

## 🧪 Post-Rollback Verification

### Immediate Checks (0-5 minutes)
```bash
# 1. Health check endpoint
curl https://my-project-smart-hiring.onrender.com/api/health

# 2. Login test
curl -X POST https://my-project-smart-hiring.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# 3. List jobs
curl https://my-project-smart-hiring.onrender.com/api/jobs/list \
  -H "Authorization: Bearer <token>"
```

### Smoke Tests (5-10 minutes)
- [ ] User login works
- [ ] Job list loads
- [ ] Application submission works
- [ ] Quiz taking functional
- [ ] Email notifications sent

### Monitoring (10-30 minutes)
- [ ] Error rate < 1%
- [ ] Response times < 2s
- [ ] No new errors in Sentry
- [ ] Database queries performing normally
- [ ] Cache hit rate > 60%

---

## 📊 Monitoring During Rollback

### Render Logs
```bash
# View live logs in Render Dashboard
# Services → smart-hiring-system → Logs tab
```

### Sentry Errors
1. Go to [Sentry Dashboard](https://sentry.io)
2. Check error rate graph
3. Verify no new critical errors

### Database Performance
```bash
# MongoDB Atlas → Metrics tab
# Check:
# - Connections
# - Query execution time
# - CPU/Memory usage
```

---

## 📢 Communication Protocol

### Incident Start
```
🚨 INCIDENT ALERT - Production Rollback Initiated

Severity: P0 (Critical)
Issue: [Brief description]
Impact: [User impact]
Rollback Method: [Git revert / Render / Manual]
ETA: [X minutes]

Status Page: [Update status page if exists]
Lead: @[your-name]
```

### Rollback In Progress
```
🔄 ROLLBACK IN PROGRESS

Current Step: [Database restore / Code deploy / Verification]
Progress: [X/Y complete]
Current Downtime: [X minutes]
```

### Rollback Complete
```
✅ ROLLBACK COMPLETE - System Restored

Version: Rolled back to [version]
Downtime: [X minutes]
Status: Monitoring for stability

Post-Mortem: [Link to incident doc]
Next Steps: [Investigation / Hotfix / etc]
```

---

## 🔍 Post-Mortem Template

**Create after rollback:**

```markdown
# Post-Mortem: [Date] Production Rollback

## Timeline
- **[Time]** - Bad deploy initiated
- **[Time]** - Issue detected
- **[Time]** - Rollback initiated
- **[Time]** - System restored
- **[Time]** - Verification complete

## Impact
- Downtime: X minutes
- Users affected: ~X
- Transactions lost: X
- Data integrity: [OK / Issues]

## Root Cause
[Detailed analysis of what went wrong]

## Resolution
[What was done to fix]

## Lessons Learned
1. [What went well]
2. [What could be improved]
3. [What we'll change]

## Action Items
- [ ] [Preventive measure 1] - Owner: [Name]
- [ ] [Process improvement] - Owner: [Name]
- [ ] [Monitoring enhancement] - Owner: [Name]
```

---

## 🛡️ Rollback Prevention

### Pre-Deploy Checklist
- [ ] All tests passing
- [ ] Staging tested for 1 hour
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Team notified of deploy

### Canary Deployment (Future)
```bash
# Deploy to 10% of traffic first
# Monitor for 30 minutes
# If stable, deploy to 100%
```

### Feature Flags (Future)
```python
if feature_enabled('new_assessment_ui'):
    return new_ui()
else:
    return old_ui()
```

---

## 📞 Emergency Contacts

**Immediate Response Team:**
- **Tech Lead:** [Phone/Slack]
- **Database Admin:** [Phone/Slack]
- **DevOps:** [Phone/Slack]

**Escalation Path:**
1. On-call engineer (respond within 5 min)
2. Tech lead (respond within 15 min)
3. CTO (respond within 30 min)

**External Services:**
- **Render Support:** https://render.com/support
- **MongoDB Atlas Support:** https://support.mongodb.com
- **SendGrid Status:** https://status.sendgrid.com

---

## 📚 Related Documentation

- **QA Checklist:** `QA_CHECKLIST.md`
- **Backup Guide:** `BACKUP_GUIDE.md`
- **Security Runbook:** `SECURITY_RUNBOOK.md`
- **Incident Response:** `INCIDENT_RESPONSE.md`

---

**Last Updated:** December 2025  
**Version:** 1.0  
**Maintained By:** DevOps Team
