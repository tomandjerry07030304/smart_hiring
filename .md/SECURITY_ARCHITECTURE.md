# Smart Hiring System - Security & Architecture Guide

## 🏗️ Architecture Overview (Version 2.0 - Enterprise Edition)

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│  (Web Browser, Mobile App, API Consumers)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│  • CORS Protection                                           │
│  • Rate Limiting                                             │
│  • Security Headers (HSTS, CSP, X-Frame-Options)            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 Authentication Layer                         │
│  • JWT-based Authentication                                  │
│  • 2FA (TOTP) for Admin/Recruiter                           │
│  • Session Management                                        │
│  • Password Hashing (bcrypt)                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Authorization Layer (RBAC)                      │
│  • Role-Based Access Control                                │
│  • Permission Checking                                       │
│  • Resource-Level Authorization                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼               ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  Application │ │  Worker  │ │    Redis     │
│   Services   │ │  Queue   │ │   (Cache &   │
│              │ │          │ │    Queue)    │
│ • Jobs       │ │ • Resume │ │              │
│ • Candidates │ │   Parsing│ │ • Job Queue  │
│ • Assessment │ │ • Email  │ │ • Caching    │
│ • Analytics  │ │   Sending│ │ • Sessions   │
│ • Audit      │ │ • ML     │ │              │
│ • DSR/GDPR   │ │   Scoring│ │              │
└──────┬───────┘ └────┬─────┘ └──────┬───────┘
       │              │               │
       └──────────────┼───────────────┘
                      ▼
         ┌────────────────────────┐
         │   MongoDB Database     │
         │                        │
         │  • users               │
         │  • jobs                │
         │  • candidates          │
         │  • applications        │
         │  • audit_logs          │
         │  • dsr_logs            │
         └────────────────────────┘
```

## 🔐 Security Features

### 1. Authentication & Authorization

#### Two-Factor Authentication (2FA)
- **TOTP-based** authentication using `pyotp`
- QR code generation for easy setup
- Backup codes for account recovery
- **Mandatory** for admin and recruiter accounts

**Implementation:**
```python
from backend.security.two_factor_auth import TwoFactorAuth

# Generate secret for user
secret = TwoFactorAuth.generate_secret()

# Generate QR code
provisioning_uri = TwoFactorAuth.get_provisioning_uri(secret, user_email)
qr_code = TwoFactorAuth.generate_qr_code(provisioning_uri)

# Verify token
is_valid = TwoFactorAuth.verify_token(secret, user_token)
```

#### Role-Based Access Control (RBAC)

**Roles:**
- **Admin**: Full system access
- **Company**: Job management, candidate review
- **Hiring Manager**: Limited review access
- **Recruiter**: Job posting and candidate sourcing
- **Candidate**: Apply to jobs, view own data
- **Auditor**: Read-only compliance access

**Permissions:**
```python
from backend.security.rbac import require_permission, Permissions

@app.route('/api/candidates')
@require_permission(Permissions.VIEW_CANDIDATES)
def get_candidates():
    # Only users with VIEW_CANDIDATES permission can access
    pass
```

### 2. Rate Limiting

Protects against brute force attacks and DDoS:

```python
from backend.security.rate_limiter import rate_limit, strict_rate_limit

@app.route('/api/auth/login')
@strict_rate_limit  # 5 requests per minute
def login():
    pass

@app.route('/api/jobs')
@rate_limit(max_requests=60, window_seconds=60)  # 60 req/min
def get_jobs():
    pass
```

### 3. Data Encryption

**PII Field Encryption:**
```python
from backend.security.encryption import encrypt_pii_fields, decrypt_pii_fields

# Before storing in database
candidate_data = encrypt_pii_fields({
    'name': 'John Doe',
    'ssn': '123-45-6789',
    'phone_number': '+1-555-1234'
})

# When retrieving
decrypted_data = decrypt_pii_fields(candidate_data)
```

**Encrypted Fields:**
- SSN / National ID
- Phone numbers
- Date of birth
- Physical addresses
- Salary expectations

### 4. File Security

#### Features:
- **Allowed file types**: PDF, DOC, DOCX, TXT, RTF
- **File size limits**: 10 MB for resumes
- **Secure filename generation**
- **MIME type validation**
- **Virus scanning** (optional, requires ClamAV)
- **Signed URLs** for secure downloads

**Usage:**
```python
from backend.security.file_security import file_security_manager

# Validate and scan file
is_allowed = file_security_manager.is_allowed_file(filename, 'resume')
is_safe, threat = file_security_manager.scan_file_for_viruses(file_path)

# Generate signed URL (expires in 24 hours)
signed_url, expiry = file_security_manager.generate_signed_url(file_path)
```

## 🔄 Background Workers

### Queue System

**Architecture:**
```
Flask App → Redis Queue → Worker Threads → Process Jobs
```

**Job Types:**
1. **Resume Parsing**: Extract skills, experience, education
2. **Email Sending**: Async email notifications
3. **Analytics Aggregation**: Pre-compute metrics
4. **ML Scoring**: Batch candidate scoring
5. **Audit Processing**: Compliance reporting

**Usage:**
```python
from backend.workers.queue_manager import queue_manager

# Enqueue a job
job_id = queue_manager.enqueue_job(
    queue_name=queue_manager.RESUME_PARSING_QUEUE,
    job_type='resume_parsing',
    data={
        'candidate_id': candidate_id,
        'file_path': resume_path
    },
    priority=1
)

# Check job status
status = queue_manager.get_job_status(job_id)
```

### Caching

**Redis Caching Layer:**
```python
from backend.workers.queue_manager import queue_manager

# Cache data for 5 minutes
queue_manager.cache_set('job_list', jobs, ttl_seconds=300)

# Retrieve cached data
cached_jobs = queue_manager.cache_get('job_list')
```

## 🌍 GDPR Compliance

### Data Subject Rights

#### 1. Right to Access (Article 15)
**Endpoint:** `POST /api/dsr/export`

Exports all user data in JSON format:
- User profile
- Applications
- Assessment results
- Audit logs

```bash
curl -X POST https://api.example.com/api/dsr/export \
  -H "Authorization: Bearer <token>"
```

#### 2. Right to Erasure (Article 17)
**Endpoint:** `POST /api/dsr/delete`

Deletes all user data:
```json
{
  "user_id": "user123",
  "confirmation": "DELETE"
}
```

#### 3. Data Anonymization
**Endpoint:** `POST /api/dsr/anonymize`

Anonymizes PII while preserving analytics:
```json
{
  "user_id": "user123"
}
```

#### 4. Consent Management
**Endpoints:**
- `GET /api/dsr/consent` - Get consent status
- `POST /api/dsr/consent` - Update consent

```json
{
  "data_processing": true,
  "marketing_emails": false,
  "analytics": true,
  "third_party_sharing": false
}
```

### Audit Trail

All data operations are logged:
```python
# Automatically logged by DSR endpoints
{
  "activity_type": "data_export",
  "requester_id": "admin123",
  "target_user_id": "user456",
  "timestamp": "2025-11-29T10:30:00Z",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

## ⚙️ Configuration

### Environment Variables

**Critical Settings:**
```bash
# Security (REQUIRED for production)
JWT_SECRET_KEY=<strong-random-key>
ENCRYPTION_KEY=<32-byte-base64-key>

# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
REDIS_URL=redis://localhost:6379/0

# Features
ENABLE_2FA=true
ENABLE_BACKGROUND_WORKERS=true
ENABLE_VIRUS_SCAN=false

# GDPR
GDPR_MODE=true
DATA_RETENTION_DAYS=2555
```

### Generate Secure Keys

```python
# JWT Secret
import secrets
print(secrets.token_hex(32))

# Encryption Key (for Fernet)
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

## 📊 Monitoring & Observability

### Logging

Structured logging throughout the application:
```python
import logging
logger = logging.getLogger(__name__)

logger.info("✅ Operation successful")
logger.warning("⚠️ Potential issue detected")
logger.error("❌ Operation failed")
```

### Metrics to Monitor

**Application Metrics:**
- Request rate (req/min)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Queue depth
- Cache hit rate

**Business Metrics:**
- Active users
- Job postings
- Applications submitted
- Time-to-hire
- Candidate drop-off rate

### Health Check

```bash
curl https://api.example.com/api/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "workers": "running",
  "environment": "production"
}
```

## 🚀 Deployment

### Prerequisites

1. **Python 3.9+**
2. **MongoDB** (Atlas or self-hosted)
3. **Redis** (optional but recommended)
4. **ClamAV** (optional, for virus scanning)

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
cp .env.template .env
# Edit .env with your settings

# 3. Initialize database
python scripts/init_db_simple.py

# 4. Start application
python backend/app.py

# 5. Start workers (separate process)
python backend/workers/job_processor.py
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start workers and app
CMD python backend/workers/job_processor.py & \
    python backend/app.py
```

### Production Checklist

- [ ] Set strong `JWT_SECRET_KEY`
- [ ] Set `ENCRYPTION_KEY` for PII
- [ ] Configure Redis for caching/queuing
- [ ] Enable 2FA for admin accounts
- [ ] Set up SSL/TLS certificates
- [ ] Configure CORS for your domain
- [ ] Enable rate limiting
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure backups
- [ ] Test DSR endpoints
- [ ] Review RBAC permissions
- [ ] Configure virus scanning (if needed)

## 🧪 Testing

### Security Testing

```bash
# 1. Test rate limiting
for i in {1..10}; do
  curl https://api.example.com/api/auth/login
done

# 2. Test 2FA
python scripts/test_2fa.py

# 3. Test DSR endpoints
python scripts/test_dsr.py
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 https://api.example.com/api/jobs

# Using Locust
locust -f tests/load_test.py
```

## 📈 Performance Optimization

### Database Indexing

```javascript
// MongoDB indexes
db.applications.createIndex({ "candidate_id": 1, "job_id": 1 })
db.applications.createIndex({ "status": 1, "created_at": -1 })
db.audit_logs.createIndex({ "timestamp": -1 })
db.audit_logs.createIndex({ "user_id": 1, "event_type": 1 })
```

### Caching Strategy

**What to Cache:**
1. Job listings (5 minutes)
2. Candidate rankings (10 minutes)
3. Analytics metrics (15 minutes)
4. User permissions (1 hour)

**Cache Invalidation:**
- On job update → invalidate job cache
- On application status change → invalidate candidate cache
- On role change → invalidate permission cache

## 🔒 Security Best Practices

1. **Never log sensitive data** (passwords, tokens, PII)
2. **Use parameterized queries** to prevent injection
3. **Validate all inputs** on server side
4. **Encrypt PII fields** before storage
5. **Use HTTPS only** in production
6. **Rotate JWT secrets** periodically
7. **Monitor for suspicious activity**
8. **Keep dependencies updated**
9. **Use secure headers** (HSTS, CSP, etc.)
10. **Implement least privilege** access control

## 📞 Support & Maintenance

### Incident Response

**Security Incident Playbook:**
1. Isolate affected systems
2. Review audit logs
3. Identify scope of breach
4. Notify affected users (if required)
5. Patch vulnerability
6. Document incident
7. Update security measures

### Regular Maintenance

**Weekly:**
- Review error logs
- Check queue health
- Monitor performance metrics

**Monthly:**
- Update dependencies
- Review access logs
- Test backup restoration
- Generate compliance reports

**Quarterly:**
- Security audit
- Penetration testing
- Update documentation
- Review RBAC roles

## 📚 API Documentation

See `API_SECURITY.md` for detailed API documentation including:
- Authentication flow
- 2FA setup process
- DSR endpoint specifications
- Rate limiting details
- Error codes and responses

## 🎯 Roadmap

**Completed (v2.0):**
- ✅ Background worker system
- ✅ Enhanced RBAC
- ✅ 2FA implementation
- ✅ File security
- ✅ GDPR compliance (DSR)
- ✅ Rate limiting
- ✅ PII encryption
- ✅ Redis caching

**Planned (v2.1+):**
- ⏳ ML explainability (SHAP/LIME)
- ⏳ Model drift monitoring
- ⏳ S3 integration
- ⏳ Video interview processing
- ⏳ Advanced analytics (pre-aggregation)
- ⏳ Multi-tenant support
- ⏳ SSO/SAML integration
- ⏳ Mobile app (PWA)

---

**Version:** 2.0.0 Enterprise Edition  
**Last Updated:** November 29, 2025  
**License:** Proprietary
