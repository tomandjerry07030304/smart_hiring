# 🎯 Smart Hiring System

A comprehensive full-stack web application for managing job postings, candidate applications, assessments, and hiring workflows.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-success)
![Live](https://img.shields.io/badge/Status-Live-success)

**🌐 Live Demo**: https://my-project-smart-hiring.onrender.com

## 🌟 Features

### 👥 User Management
- **Multi-role System**: Admin, Company/Recruiter, and Candidate roles
- **Secure Authentication**: JWT-based authentication with bcrypt password hashing
- **Profile Management**: Comprehensive user profiles with resume uploads

### 💼 Job Management
- **Job Posting**: Create and manage job listings with detailed requirements
- **Application Tracking**: Real-time status management (Applied, Under Review, Interview Scheduled, Rejected, Accepted)
- **Advanced Filtering**: Search jobs by title, skills, location

### 📝 Assessment System (NEW!)
- **Question Bank**: Manage question pools by category and difficulty
- **Quiz Builder**: Create custom quizzes with configurable settings
- **Timed Assessments**: Countdown timer with auto-submit
- **Auto-Grading**: Automatic scoring for MCQ, true/false, short answer
- **Analytics**: Comprehensive performance analytics for recruiters

### 📧 Email Notifications (NEW!)
- **Transactional**: Welcome, confirmations, status updates
- **Marketing**: Job alerts, newsletters (opt-in/opt-out)
- **Preferences**: User-controlled notification settings
- **SendGrid Integration**: Professional email templates

### 🎨 Modern UI/UX (NEW!)
- **Loading States**: Skeleton screens with shimmer animations
- **Empty States**: Friendly designs with action prompts
- **Toast Notifications**: 4 types (success/error/warning/info)
- **Micro-interactions**: Hover effects, ripples, transitions
- **Accessibility**: WCAG compliant with keyboard navigation
- **Dark Mode**: System preference detection

## 🏗️ Architecture

### Backend
- **Framework**: Flask 3.0
- **Language**: Python 3.13
- **Database**: MongoDB Atlas
- **Auth**: JWT (Flask-JWT-Extended)
- **Email**: SendGrid API
- **Security**: bcrypt password hashing

### Frontend
- **Stack**: HTML5, CSS3, Vanilla JavaScript
- **Design**: Custom CSS with modern design system
- **Icons**: Unicode + custom SVG

### Deployment
- **Platform**: Render.com
- **CI/CD**: Auto-deploy from GitHub
- **URL**: https://my-project-smart-hiring.onrender.com

## 📂 Project Structure

```
smart-hiring-system/
├── backend/
│   ├── models/
│   │   └── assessment.py          # Quiz models
│   ├── routes/
│   │   ├── auth_routes.py         # Authentication
│   │   ├── job_routes.py          # Job management
│   │   ├── candidate_routes.py    # Applications
│   │   ├── company_routes.py      # Recruiter features
│   │   ├── assessment_routes.py   # Quizzes (NEW)
│   │   └── email_routes.py        # Email prefs (NEW)
│   ├── email_service.py           # SendGrid (NEW)
│   ├── app.py                     # Flask app
│   └── requirements.txt
├── frontend/
│   ├── index.html                 # Main entry
│   ├── questions.html             # Question bank (NEW)
│   ├── quizzes.html               # Quiz management (NEW)
│   ├── take-quiz.html             # Quiz interface (NEW)
│   ├── email-preferences.html     # Email settings (NEW)
│   ├── styles.css                 # Main styles
│   ├── ui-enhancements.css        # Modern UI (NEW)
│   ├── ui-utils.js                # UI utilities (NEW)
│   ├── ui-enhancements.js         # Enhancement layer (NEW)
│   ├── app.js                     # Main logic
│   ├── candidate.js
│   ├── company.js
│   └── admin.js
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- MongoDB Atlas account
- SendGrid account
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/SatyaSwaminadhYedida03/my-project-s1.git
cd my-project-s1/smart-hiring-system

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
# Create .env file with:
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
JWT_SECRET_KEY=your-secret-key
SENDGRID_API_KEY=your-sendgrid-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Run application
python app.py

# Access at http://localhost:5000
```

## 📚 API Documentation

### Authentication
```http
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/profile
```

### Jobs
```http
POST /api/jobs/create
GET  /api/jobs/list
GET  /api/jobs/<id>
PUT  /api/jobs/<id>
DELETE /api/jobs/<id>
```

### Applications
```http
POST /api/candidates/apply
GET  /api/candidates/applications
PUT  /api/candidates/applications/<id>/status
```

### Assessments (NEW)
```http
POST /api/assessments/questions
GET  /api/assessments/questions
POST /api/assessments/quizzes
GET  /api/assessments/quizzes
POST /api/assessments/quizzes/<id>/start
POST /api/assessments/attempts/<id>/submit
GET  /api/assessments/attempts/<id>
GET  /api/assessments/quizzes/<id>/analytics
```

### Email (NEW)
```http
GET  /api/email/preferences
PUT  /api/email/preferences
```

## 🎨 Design System

### Colors
- **Primary**: #4F46E5 (Indigo)
- **Secondary**: #7c3aed (Purple)
- **Success**: #10b981
- **Error**: #ef4444
- **Warning**: #f59e0b

### Typography
- **Font**: System fonts (-apple-system, Segoe UI, Roboto)
- **Base Size**: 16px

### Spacing
- 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px

## 📖 User Guide

### For Candidates
1. Register with email and password
2. Browse jobs in "Browse Jobs" tab
3. Apply to jobs with one click
4. Take assessments when assigned
5. Track application status
6. Manage email preferences

### For Recruiters
1. Create company account
2. Post jobs with requirements
3. Create question bank
4. Build quizzes for assessments
5. Review applications
6. Update application status
7. View quiz analytics

## 🔒 Security

- bcrypt password hashing
- JWT token authentication
- CORS protection
- Input validation
- MongoDB query parameterization
- HTTPS enforced in production
- Environment variable protection

## 🌐 Deployment

### Render.com
1. Connect GitHub repository
2. Set build command: `cd backend && pip install -r requirements.txt`
3. Set start command: `cd backend && gunicorn app:app`
4. Add environment variables
5. Deploy (auto-deploy on push to main)

## 📝 Environment Variables

| Variable | Description |
|----------|-------------|
| `MONGO_URI` | MongoDB connection string |
| `JWT_SECRET_KEY` | JWT secret for tokens |
| `SENDGRID_API_KEY` | SendGrid API key |
| `SENDGRID_FROM_EMAIL` | Sender email address |

## 🧪 Testing

### Test Accounts
```
Admin:
Email: admin@test.com
Password: admin123

Company:
Email: company@test.com
Password: company123

Candidate:
Email: candidate@test.com
Password: candidate123
```

### Manual Test Checklist
- [x] User registration (all roles)
- [x] Login/authentication
- [x] Job posting creation
- [x] Job application submission
- [x] Application status updates
- [x] Quiz creation & taking
- [x] Auto-grading accuracy
- [x] Email notifications
- [x] Email preferences
- [x] Profile updates
- [x] Responsive design
- [x] Accessibility features
- [x] Dark mode

## 🚀 Recent Updates

### v2.0.0 (Current)
- ✨ Complete assessment/quiz system with 11 endpoints
- ✨ Email notification system with SendGrid
- ✨ Application status management
- ✨ Modern UI with loading/empty states
- ✨ Toast notifications
- ✨ Accessibility improvements
- ✨ Dark mode support
- 🐛 Fixed JWT authentication issues
- 🎨 Enhanced responsive design

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file

## 👨‍💻 Author

**Satya Swaminadh Yedida**
- GitHub: [@SatyaSwaminadhYedida03](https://github.com/SatyaSwaminadhYedida03)
- Repository: [my-project-s1](https://github.com/SatyaSwaminadhYedida03/my-project-s1)

## 🙏 Acknowledgments

- Flask & Python community
- MongoDB Atlas
- Render.com
- SendGrid
- Open-source contributors

---

**Built with ❤️ using Flask, MongoDB, and Modern Web Technologies**

**⭐ Star this repo if you find it useful!**
