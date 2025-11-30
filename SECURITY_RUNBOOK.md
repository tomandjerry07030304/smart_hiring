# Security Implementation Runbook

## 🔒 Production Security Checklist

### Immediate Actions (Before Going Live)

#### 1. Environment Secrets
Generate and set secure secrets in Render dashboard:

```powershell
# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY (32 bytes, base64 encoded)
python -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

Required environment variables in Render:
- ✅ `JWT_SECRET_KEY` - JWT token signing
- ✅ `SECRET_KEY` - Flask secret key
- ✅ `ENCRYPTION_KEY` - PII field encryption
- ✅ `MONGODB_URI` - MongoDB Atlas connection
- ✅ `SENDGRID_API_KEY` - Email service
- ✅ `SENDGRID_FROM_EMAIL` - Verified sender email
- ⚠️ `SENTRY_DSN` - Error tracking (optional but recommended)

#### 2. MongoDB Atlas Security
- ✅ Enable IP allowlist (add Render IPs or your deployment IPs)
- ✅ Use strong database password (20+ characters, mixed case, symbols)
- ✅ Enable encryption at rest
- ✅ Configure automated backups (daily recommended)
- ✅ Enable audit logging
- ✅ Create read-only user for analytics queries

#### 3. Rate Limiting Configuration
Already implemented via `backend/middleware/rate_limiter.py`:
- Login: 5 attempts per 15 minutes per IP
- Registration: 10 per hour per IP
- Password reset: 3 per hour per email
- API endpoints: 100 requests per minute per user

#### 4. CORS Configuration
Update `backend/app.py` allowed origins:
```python
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'https://yourdomain.com').split(',')
```

Set in Render:
```
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### 5. HTTPS & TLS
- ✅ Render provides automatic HTTPS
- ✅ Configure custom domain with TLS certificate
- ✅ Enable HSTS (already configured in app.py)
- ✅ Set secure cookie flags for JWT

### Security Features Already Implemented

#### Authentication & Authorization
- ✅ JWT with secure token signing
- ✅ bcrypt password hashing (12 rounds)
- ✅ Role-based access control (RBAC)
- ✅ Password complexity requirements
- ✅ Account lockout after failed attempts

#### Data Protection
- ✅ Input validation and sanitization
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS protection via sanitization
- ✅ CSRF protection headers
- ✅ PII field encryption support

#### Network Security
- ✅ Security headers (CSP, X-Frame-Options, X-Content-Type-Options)
- ✅ CORS properly configured
- ✅ Rate limiting on sensitive endpoints
- ✅ Request timeout configuration

### Monitoring & Incident Response

#### Sentry Integration
1. Create Sentry account: https://sentry.io
2. Create new Python/Flask project
3. Get DSN from Settings → Client Keys
4. Set `SENTRY_DSN` environment variable in Render
5. Verify events are captured

#### Log Monitoring
Check logs regularly for:
- Failed authentication attempts
- Rate limit violations
- 500 errors
- Unusual traffic patterns

View logs:
```bash
# Via Render dashboard or CLI
render logs --tail
```

#### Backup Verification
Test database restore monthly:
1. Download backup from MongoDB Atlas
2. Restore to test cluster
3. Verify data integrity
4. Document restore time

### Compliance (GDPR)

#### Data Subject Rights
Already implemented:
- ✅ Right to access (`/api/dsr/export`)
- ✅ Right to erasure (`/api/dsr/delete`)
- ✅ Data portability (JSON export)
- ✅ Consent management

#### Audit Trail
- ✅ All DSR requests logged
- ✅ Admin actions tracked
- ✅ Application status changes recorded

#### Data Retention
Configure retention policy:
```
DATA_RETENTION_DAYS=2555  # 7 years default
```

### Penetration Testing Checklist

Run before production launch:
- [ ] Test SQL injection on all inputs
- [ ] Test XSS in text fields
- [ ] Test authentication bypass
- [ ] Test authorization escalation
- [ ] Test rate limit enforcement
- [ ] Test file upload vulnerabilities
- [ ] Test API abuse scenarios
- [ ] Test session management
- [ ] Verify HTTPS enforcement
- [ ] Test password reset flow

Tools:
- OWASP ZAP
- Burp Suite
- Postman security tests

### Incident Response Plan

#### Security Breach Response
1. **Detect**: Monitor Sentry, logs, alerts
2. **Contain**: 
   - Rotate all secrets immediately
   - Block attacker IP addresses
   - Disable compromised accounts
3. **Investigate**:
   - Review audit logs
   - Check database for unauthorized access
   - Identify affected users
4. **Notify**:
   - Inform affected users within 72 hours (GDPR)
   - Report to authorities if required
5. **Recover**:
   - Restore from clean backup if needed
   - Apply security patches
   - Update access controls
6. **Review**:
   - Document incident
   - Update security measures
   - Conduct post-mortem

#### Emergency Contacts
- Security Team Lead: [Add contact]
- Database Admin: [Add contact]
- Legal/Compliance: [Add contact]
- Sentry Alert: [Email/Slack channel]

### Regular Security Maintenance

#### Weekly
- Review Sentry error reports
- Check rate limit violations
- Monitor failed login attempts

#### Monthly
- Update dependencies (`pip list --outdated`)
- Review user access permissions
- Test backup restoration
- Review audit logs

#### Quarterly
- Rotate JWT secret keys
- Security audit & penetration test
- Review and update RBAC policies
- Update security documentation

### Dependency Security

Scan for vulnerabilities:
```bash
# Install safety
pip install safety

# Check for known vulnerabilities
safety check -r requirements.txt

# Update vulnerable packages
pip install --upgrade <package>
```

CI/CD already includes `safety check` in GitHub Actions.

### Additional Hardening (Future)

High priority:
- [ ] Implement 2FA for admin accounts
- [ ] Add Web Application Firewall (WAF)
- [ ] Configure DDoS protection (Cloudflare)
- [ ] Add honeypot fields for bot detection
- [ ] Implement session expiration
- [ ] Add IP geolocation blocking for high-risk regions
- [ ] Enable Redis for distributed rate limiting
- [ ] Add security.txt file

Medium priority:
- [ ] Implement Content Security Policy reporting
- [ ] Add Subresource Integrity (SRI) for CDN assets
- [ ] Configure HTTP Public Key Pinning
- [ ] Add certificate transparency monitoring
- [ ] Implement automated security scanning

### Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Flask Security Guide: https://flask.palletsprojects.com/en/latest/security/
- MongoDB Security Checklist: https://docs.mongodb.com/manual/administration/security-checklist/
- GDPR Compliance: https://gdpr.eu/
- Python Security: https://python.readthedocs.io/en/stable/library/security_warnings.html

---
**Last Updated**: November 2025  
**Review Frequency**: Quarterly  
**Owner**: Security Team
