# Security Protocols & Access Control

## 🔒 Repository Access Control

### Private Repository Status
- Repository: `my-project-s1` (SatyaSwaminadhYedida03)
- Visibility: **PRIVATE** (set in GitHub settings)
- Access: Restricted to authorized collaborators only

### Authorized Personnel
Only the following individuals have access:
- Repository Owner: SatyaSwaminadhYedida03
- Authorized Developers: (Add as needed)

### Adding Collaborators
1. Go to: Settings → Collaborators and teams
2. Invite only trusted developers
3. Assign appropriate permissions:
   - **Read**: View code only
   - **Write**: Push changes (requires approval)
   - **Admin**: Full access (owner only)

---

## 📜 License & Legal Protection

### Proprietary License
- Software is **NOT open-source**
- All rights reserved © 2025 Smart Hiring System
- See [LICENSE](../LICENSE) file for complete terms

### Usage Restrictions
❌ **PROHIBITED without written authorization:**
- Using the software
- Copying or distributing code
- Modifying or creating derivatives
- Reverse engineering
- Commercial deployment
- Removing copyright notices

✅ **ALLOWED with authorization:**
- Internal development by authorized team
- Testing in development environments
- Deployment with valid license key

---

## 🔐 Deployment Authorization System

### License-Based Access Control
The system includes three layers of protection:

#### 1. License Key Validation
- Each production deployment requires unique license key
- Keys are generated using `scripts/generate_license.py`
- Without valid key, application refuses to start

#### 2. Domain Authorization
- Only pre-approved domains can run the application
- Configured in `AUTHORIZED_DOMAINS` environment variable
- Prevents unauthorized hosting

#### 3. Deployment Signature
- Cryptographic signature validates license authenticity
- Generated from license key using HMAC-SHA256
- Tampering detection built-in

### Generating Deployment Licenses

```bash
# For production deployment
python scripts/generate_license.py --domain yourdomain.com --email client@email.com

# For 90-day trial
python scripts/generate_license.py --domain trial.com --email trial@email.com --days 90
```

### Environment Configuration

**Development (.env):**
```env
SKIP_LICENSE_CHECK=true
DEPLOYMENT_DOMAIN=localhost
```

**Production (.env):**
```env
DEPLOYMENT_LICENSE_KEY=generated-key-here
DEPLOYMENT_SIGNATURE=generated-signature-here
DEPLOYMENT_DOMAIN=yourdomain.com
AUTHORIZED_DOMAINS=yourdomain.com,www.yourdomain.com
SKIP_LICENSE_CHECK=false
```

---

## 🛡️ Code Protection Mechanisms

### 1. Obfuscation
- Sensitive algorithms protected using `backend/utils/code_protector.py`
- Business logic functions marked with `@protected_function`
- Configuration values encrypted in transit

### 2. Integrity Checking
- File checksums validate code hasn't been tampered
- Runtime validation prevents unauthorized modifications
- Alerts generated for integrity violations

### 3. Watermarking
- Each code distribution includes unique identifier
- Traces unauthorized leaks back to source
- Developer-specific watermarks embedded

### Protected Components
These components include additional security:
- Candidate matching algorithms
- AI interview question generation
- Scoring and ranking logic
- Assessment evaluation
- Fairness calculation methods

---

## 🚨 Security Incident Response

### Unauthorized Access Detection
If unauthorized access is detected:
1. **Immediate Actions:**
   - Revoke compromised credentials
   - Change all deployment keys
   - Regenerate license signatures
   - Audit access logs

2. **Investigation:**
   - Identify breach source
   - Assess data exposure
   - Document incident timeline
   - Contact affected parties

3. **Prevention:**
   - Update security measures
   - Implement additional monitoring
   - Review access controls
   - Train team on security

### Reporting Security Issues
- **Email:** admin@smarthiring.com
- **Subject:** SECURITY INCIDENT - [Brief Description]
- **Include:** Date/time, observed behavior, potential impact

---

## 📋 Deployment Checklist

Before deploying to production:

- [ ] Repository is set to **PRIVATE**
- [ ] Valid license key generated
- [ ] Domain authorized in license
- [ ] `.env` file configured with license
- [ ] `SKIP_LICENSE_CHECK=false` in production
- [ ] All sensitive keys rotated from development
- [ ] HTTPS enabled on domain
- [ ] Firewall rules configured
- [ ] Monitoring and logging enabled
- [ ] Backup system in place
- [ ] Security audit completed
- [ ] Team briefed on security protocols

---

## 🔑 Credential Management

### Environment Variables Security
Never commit these to git:
- `DEPLOYMENT_LICENSE_KEY`
- `DEPLOYMENT_SIGNATURE`
- `JWT_SECRET_KEY`
- `MONGODB_URI` (with credentials)
- `SMTP_PASSWORD`
- Any API keys or tokens

### Secure Storage
- Use environment variables
- Store secrets in secure vault (e.g., AWS Secrets Manager, Azure Key Vault)
- Rotate credentials regularly (every 90 days)
- Use different credentials for each environment

### Access Control
- Limit who can view production credentials
- Use service accounts for deployments
- Implement principle of least privilege
- Audit credential access regularly

---

## 📞 Contact & Authorization Requests

**For licensing and authorization:**
- Primary Email: mightyazad@gmail.com
- Alternative: admin@smarthiring.com
- Include: Company name, intended use, deployment details

**For security concerns:**
- Primary Email: mightyazad@gmail.com
- Alternative: admin@smarthiring.com
- Subject: SECURITY ISSUE
- Response time: 24-48 hours

---

## ⚖️ Legal Notice

Unauthorized access, use, distribution, or modification of this software may result in:
- Civil liability for damages
- Criminal prosecution under applicable laws
- Immediate termination of access
- Legal action to protect intellectual property

By accessing this repository, you agree to comply with all terms in the [LICENSE](../LICENSE) file and these security protocols.

---

**Last Updated:** November 16, 2025
**Version:** 1.0
**Status:** Active - Private Development Phase
