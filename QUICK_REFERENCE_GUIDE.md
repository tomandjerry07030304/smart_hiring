# 📚 Quick Reference Guide - Smart Hiring System

## 🚀 Quick Start Commands

### Development Setup
```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/smart-hiring-system.git
cd smart-hiring-system

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env
# Edit .env with your MongoDB URI, SECRET_KEY, etc.

# 5. Run application
python app.py
# Visit: http://localhost:5000
```

### Docker Setup
```bash
# 1. Build and start all services
docker-compose -f deploy/docker-compose.fixed.yml up --build

# 2. Check service status
docker-compose -f deploy/docker-compose.fixed.yml ps

# 3. View logs
docker-compose -f deploy/docker-compose.fixed.yml logs -f backend

# 4. Stop services
docker-compose -f deploy/docker-compose.fixed.yml down
```

---

## 📂 Key File Locations

| Component | File Path |
|-----------|-----------|
| **Main App** | `backend/app.py` |
| **Configuration** | `config/config.py` |
| **Database** | `backend/models/database.py` |
| **User Model** | `backend/models/user.py` |
| **Auth Routes** | `backend/routes/auth_routes.py` |
| **Job Routes** | `backend/routes/job_routes.py` |
| **ML Ranking** | `backend/services/ranking_service.py` |
| **Resume Parser** | `backend/utils/resume_parser.py` |
| **Encryption** | `backend/security/encryption.py` |
| **Frontend UI** | `frontend/` directory |
| **Docker Compose** | `deploy/docker-compose.fixed.yml` |
| **Requirements** | `requirements.txt` |
| **Tests** | `backend/tests/` directory |

---

## 🔑 Environment Variables

### Required Variables (.env)
```bash
# App Configuration
FLASK_ENV=production
SECRET_KEY=<64-character-random-string>
JWT_SECRET_KEY=<64-character-random-string>

# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/smart_hiring_db
DB_NAME=smart_hiring_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Encryption
ENCRYPTION_KEY=<base64-fernet-key>

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>

# LinkedIn OAuth
LINKEDIN_CLIENT_ID=<your-client-id>
LINKEDIN_CLIENT_SECRET=<your-client-secret>

# CORS
ALLOWED_ORIGINS=https://my-project-smart-hiring.onrender.com,http://localhost:5000
```

### Generate Secure Keys
```bash
# SECRET_KEY (64 chars)
python -c "import secrets; print(secrets.token_hex(32))"

# ENCRYPTION_KEY (Fernet)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 🛠️ Common Tasks

### Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest backend/tests/test_api.py

# Run with coverage
pytest --cov=backend --cov-report=html

# View coverage report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
```

### Database Operations
```bash
# Initialize database
python backend/scripts/init_db.py

# Seed test data
python backend/scripts/seed_db.py

# MongoDB shell
mongosh "mongodb+srv://cluster.mongodb.net" --username <user>
```

### Celery Workers
```bash
# Start Celery worker
celery -A backend.celery_config worker --loglevel=info

# Start Flower (monitoring UI)
celery -A backend.celery_config flower
# Visit: http://localhost:5555
```

### Build Desktop App
```powershell
# Build Electron app
.\build_scripts\build_electron_clean.ps1

# Build backend EXE
.\build_scripts\build_backend_exe.ps1
```

---

## 🔐 User Roles & Permissions

| Role | Can Do |
|------|--------|
| **Admin** | Everything (user management, system config) |
| **Company** | Post jobs, view applicants, hire |
| **Hiring Manager** | Review candidates, schedule interviews |
| **Recruiter** | Source candidates, conduct assessments |
| **Candidate** | Apply to jobs, take assessments, track status |
| **Auditor** | View fairness reports, audit logs (read-only) |

---

## 📊 API Endpoints Cheat Sheet

### Authentication
```bash
# Register
POST /api/auth/register
Body: { "email", "password", "full_name", "role" }

# Login
POST /api/auth/login
Body: { "email", "password", "totp_code" (if 2FA enabled) }

# Get Profile
GET /api/auth/profile
Headers: Authorization: Bearer <token>
```

### Jobs
```bash
# List jobs
GET /api/jobs?page=1&limit=20

# Get job details
GET /api/jobs/{job_id}

# Create job (company/admin)
POST /api/jobs
Body: { "title", "description", "required_skills", ... }

# Apply to job (candidate)
POST /api/jobs/{job_id}/apply
Body: multipart/form-data (resume file + cover_letter)
```

### Candidates
```bash
# Get ranked candidates (hiring manager)
GET /api/jobs/{job_id}/ranked-candidates

# Get candidate profile
GET /api/candidates/{candidate_id}

# Update candidate profile
PUT /api/candidates/{candidate_id}
```

### Assessments
```bash
# Get assessment
GET /api/assessments/{assessment_id}

# Submit assessment
POST /api/assessments/{assessment_id}/submit
Body: { "answers": [...] }
```

---

## 🐛 Troubleshooting

### Issue: "Invalid SECRET_KEY"
**Solution**: Ensure SECRET_KEY is at least 32 characters in `.env`
```bash
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

### Issue: "MongoDB connection failed"
**Solution**: Check MONGODB_URI format
```bash
# Correct format
mongodb+srv://username:password@cluster.mongodb.net/database_name

# Test connection
mongosh "YOUR_MONGODB_URI"
```

### Issue: "ModuleNotFoundError: No module named 'config'"
**Solution**: Ensure virtual environment activated and in correct directory
```bash
cd smart-hiring-system
.venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Docker container exits immediately
**Solution**: Check logs for errors
```bash
docker-compose -f deploy/docker-compose.fixed.yml logs backend
```

### Issue: "Celery worker not processing tasks"
**Solution**: Verify Redis connection
```bash
# Test Redis
redis-cli -h localhost -p 6379 ping
# Expected output: PONG
```

---

## 📝 Git Workflow

### Feature Development
```bash
# 1. Create feature branch
git checkout -b feature/my-new-feature

# 2. Make changes and commit
git add .
git commit -m "Add my new feature"

# 3. Push to remote
git push origin feature/my-new-feature

# 4. Create Pull Request on GitHub

# 5. After merge, delete branch
git branch -d feature/my-new-feature
```

### Hotfix Process
```bash
# 1. Create hotfix from main
git checkout main
git checkout -b hotfix/critical-bug

# 2. Fix and commit
git commit -m "Hotfix: Fix critical bug in auth"

# 3. Merge back to main
git checkout main
git merge --no-ff hotfix/critical-bug
git push origin main

# 4. Tag release
git tag -a v2.0.1 -m "Hotfix release v2.0.1"
git push origin v2.0.1
```

---

## 📈 Performance Optimization Tips

### Database
```javascript
// Create indexes for faster queries
db.users.createIndex({ email: 1 }, { unique: true });
db.jobs.createIndex({ status: 1, created_at: -1 });
db.applications.createIndex({ job_id: 1, ml_score: -1 });
```

### Caching
```python
# Cache expensive ML calculations
from backend.utils.cache import cache_job_rankings

rankings = get_cached_rankings(job_id) or compute_rankings(job_id)
cache_job_rankings(job_id, rankings, ttl=3600)
```

### Background Tasks
```python
# Offload heavy tasks to Celery
from backend.tasks.resume_tasks import parse_resume_task

parse_resume_task.delay(candidate_id, resume_path)
```

---

## 🔗 Useful Links

- **Live Demo**: https://my-project-smart-hiring.onrender.com
- **Documentation**: See `/docs` folder
- **API Tests**: `Smart_Hiring_API.postman_collection.json`
- **GitHub**: (Add your repo URL)
- **Contact**: mightyazad@gmail.com

---

## 📦 Dependency Versions

```txt
Flask==3.0.0
pymongo==4.6.1
redis==5.0.1
celery==5.3.4
scikit-learn==1.5.2
PyPDF2==3.0.1
python-docx==1.1.0
cryptography==41.0.7
flask-jwt-extended==4.6.0
gunicorn==21.2.0
pytest==7.4.3
```

---

## 🎯 Testing Checklist

Before deployment, test:
- [ ] User registration works
- [ ] Login with JWT returns token
- [ ] 2FA enrollment and verification
- [ ] Job posting creates successfully
- [ ] Resume upload and parsing
- [ ] Candidate ranking algorithm
- [ ] Email notifications send
- [ ] RBAC permissions enforced
- [ ] Docker containers start without errors
- [ ] All tests pass (`pytest`)

---

**Last Updated**: December 7, 2025  
**Version**: 2.0.0  
**Maintainer**: Venkat Anand
