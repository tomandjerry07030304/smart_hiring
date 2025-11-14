# 🚀 Smart Hiring System - AI-Powered Fair Recruitment Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Overview

A comprehensive, production-ready recruitment system that eliminates bias and automates hiring from job posting to onboarding. Built with AI/ML for fairness, transparency, and efficiency.

### 🎯 Key Features

#### ✅ **Complete Hiring Workflow**
- Job Posting Management
- Candidate Registration & Authentication
- Resume Upload & Parsing (PDF, DOCX, TXT)
- **Automated PII Anonymization** (NER + Regex)
- AI-Powered Skill Extraction
- Online Assessments (MCQ, Coding, Behavioral)
- Interview Scheduling
- Recruiter Analytics Dashboard

#### ✅ **Fairness & Bias Detection**
- **IBM AIF360** Integration
- Demographic Parity Analysis
- Equal Opportunity Metrics
- Disparate Impact Detection (80% Rule)
- Comprehensive Audit Reports
- Algorithmic Transparency

#### ✅ **Advanced Algorithms**
- **Career Consistency Index (CCI)** - Job stability scoring
- TF-IDF Similarity Matching
- Multi-factor Candidate Ranking
- Skill Gap Analysis

---

## 🏗️ Architecture

```
smart-hiring-system/
├── backend/
│   ├── models/          # MongoDB data models (5 files)
│   ├── routes/          # REST API endpoints (5 files, 20+ endpoints)
│   ├── services/        # Business logic (fairness, etc.)
│   ├── utils/           # Helpers (parsing, matching, CCI)
│   ├── scripts/         # DB initialization & seeding
│   └── app.py           # Flask application
├── config/              # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── API_DOCUMENTATION.md # Complete API reference
├── SETUP.md             # Installation guide
└── IMPLEMENTATION_SUMMARY.md # Feature comparison
```

**Total: 25+ Files | 3000+ Lines of Code**

---

## ⚡ Quick Start

### Option 1: Automated Setup (Recommended)
```powershell
# Windows PowerShell
.\start.ps1
```

Choose option 4 to run all setup steps automatically.

### Option 2: Manual Setup

#### 1. Install Dependencies
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

#### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your MongoDB URI
```

#### 3. Initialize Database
```bash
python backend/scripts/init_db.py
python backend/scripts/seed_db.py
```

#### 4. Run Application
```bash
python backend/app.py
```

Server runs at: **http://localhost:5000**

#### 5. Test API
```bash
python test_api.py
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SETUP.md](SETUP.md) | Detailed installation guide |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Complete API reference |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Feature comparison with PPT |

---

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `GET /api/auth/profile` - Get profile

### Jobs
- `POST /api/jobs/create` - Create job (recruiter)
- `GET /api/jobs/list` - List jobs
- `GET /api/jobs/{id}` - Get job details

### Candidates
- `POST /api/candidates/upload-resume` - Upload resume
- `POST /api/candidates/apply/{job_id}` - Apply to job
- `GET /api/candidates/applications` - My applications

### Assessments
- `POST /api/assessments/create` - Create assessment
- `POST /api/assessments/{id}/submit` - Submit answers
- `POST /api/assessments/schedule-interview` - Schedule interview

### Dashboard
- `GET /api/dashboard/analytics` - Recruitment metrics
- `GET /api/dashboard/fairness/{job_id}` - Fairness audit
- `GET /api/dashboard/transparency/{app_id}` - Transparency report

**See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for full details**

---

## 🧪 Sample Credentials (After Seeding)

```
Recruiter:
  Email: recruiter@techcorp.com
  Password: recruiter123

Candidate:
  Email: candidate1@example.com
  Password: candidate123
```

---

## 🛠️ Technologies

### Backend
- **Flask** - Web framework
- **MongoDB** - Database
- **JWT** - Authentication
- **Bcrypt** - Password hashing

### AI/ML
- **scikit-learn** - TF-IDF, Cosine Similarity
- **spaCy** - NLP & NER
- **AIF360** - Fairness metrics
- **pandas/numpy** - Data processing

### Utilities
- **PyPDF2** - PDF parsing
- **python-docx** - DOCX parsing
- **APScheduler** - Task scheduling

---

## 📊 Key Algorithms

### 1. Career Consistency Index (CCI)
```python
CCI = 0.4×tenure + 0.3×frequency + 0.2×progression + 0.1×gaps
```

### 2. Candidate Score
```python
Score = 0.5×TF-IDF_sim + 0.3×skill_match + 0.2×CCI
```

### 3. Fairness Metrics
- **Demographic Parity**: |P(Ŷ=1|D=A) - P(Ŷ=1|D=B)| < 0.1
- **Disparate Impact**: P(Ŷ=1|D=A) / P(Ŷ=1|D=B) >= 0.8
- **Equal Opportunity**: |TPR(A) - TPR(B)| < 0.1

---

## 🎯 Features vs Presentation

| Feature (PPT Slide 15) | Status |
|------------------------|--------|
| Job Posting | ✅ |
| Candidate Registration | ✅ |
| Resume Upload & Anonymization | ✅ |
| NLP Skill Extraction | ✅ |
| Candidate Assessments | ✅ |
| Interview Scheduling | ✅ |
| Recruiter Dashboard | ✅ |
| Fairness Auditing | ✅ |
| CCI Calculation | ✅ |
| Transparency Reports | ✅ |

**Implementation: 95%+ Complete** 🎉

---

## 🔜 Future Enhancements

- [ ] React.js Frontend
- [ ] LinkedIn OAuth Integration
- [ ] Email Notifications
- [ ] Video Interview Integration
- [ ] Docker Deployment
- [ ] CI/CD Pipeline

---

## 👥 Team

- **S. Mohana Swarupa** (22VV1A0547)
- **N. Praneetha** (22VV1A0542)
- **Y.S.S.D.V.Satya Swaminadh** (22VV1A0555)
- **Ch. Renuka Sri** (22VV1A0509)

**Project Guide**: Mr. R.D.D.V. SIVARAM

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🤝 Contributing

This is an academic project. For suggestions or improvements, please contact the team.

---

## 📞 Support

For issues:
1. Check [SETUP.md](SETUP.md) for installation help
2. Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API usage
3. See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for feature details

---

**Built with ❤️ for Fair and Transparent Hiring**
