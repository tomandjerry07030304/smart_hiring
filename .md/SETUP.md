# Smart Hiring System - Setup Guide

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.10 or higher**
   ```bash
   python --version
   ```

2. **MongoDB 6.0 or higher**
   - Download from: https://www.mongodb.com/try/download/community
   - Or use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas

3. **Git** (optional, for version control)

---

## Installation Steps

### 1. Clone or Download Project
```bash
cd "C:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system"
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Download spaCy Language Model
```bash
python -m spacy download en_core_web_sm
```

### 6. Configure Environment Variables

Create `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
# Database
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=smart_hiring_db

# JWT
JWT_SECRET_KEY=your-secret-key-change-this
JWT_ACCESS_TOKEN_EXPIRES=3600

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-flask-secret-key

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 7. Start MongoDB

**Option A: Local MongoDB**
```bash
# Start MongoDB service
mongod --dbpath C:\data\db
```

**Option B: MongoDB Atlas (Cloud)**
Update `.env`:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

### 8. Initialize Database (Optional)

Create initial collections and indexes:
```bash
python backend/scripts/init_db.py
```

### 9. Run the Application
```bash
python backend/app.py
```

You should see:
```
🚀 Starting Smart Hiring System API
📍 Environment: development
🔗 Running on: http://localhost:5000
🗄️  Database: smart_hiring_db
```

---

## Testing the API

### 1. Health Check
```bash
curl http://localhost:5000/api/health
```

### 2. Register a User
```powershell
$body = @{
    email = "test@example.com"
    password = "password123"
    full_name = "Test User"
    role = "candidate"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/register" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

### 3. Login
```powershell
$body = @{
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$token = $response.access_token
Write-Host "Token: $token"
```

### 4. Test Protected Endpoint
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/auth/profile" `
    -Method Get `
    -Headers @{Authorization = "Bearer $token"}
```

---

## Project Structure

```
smart-hiring-system/
├── backend/
│   ├── models/               # Database models
│   │   ├── database.py       # MongoDB connection
│   │   ├── user.py           # User & Candidate models
│   │   ├── job.py            # Job & Application models
│   │   ├── assessment.py     # Assessment & Interview models
│   │   └── fairness.py       # Fairness audit models
│   │
│   ├── routes/               # API endpoints
│   │   ├── auth_routes.py    # Authentication
│   │   ├── job_routes.py     # Job management
│   │   ├── candidate_routes.py # Candidate operations
│   │   ├── assessment_routes.py # Assessments & interviews
│   │   └── dashboard_routes.py # Analytics & fairness
│   │
│   ├── services/             # Business logic
│   │   └── fairness_service.py # Bias detection
│   │
│   ├── utils/                # Helper functions
│   │   ├── resume_parser.py  # Resume text extraction
│   │   ├── matching.py       # Candidate matching
│   │   └── cci_calculator.py # Career consistency index
│   │
│   └── app.py                # Flask application
│
├── config/
│   └── config.py             # Configuration settings
│
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── README.md                 # Project overview
├── API_DOCUMENTATION.md      # API reference
└── SETUP.md                  # This file
```

---

## Common Issues & Solutions

### Issue: MongoDB Connection Failed
**Solution:**
- Ensure MongoDB is running
- Check MONGODB_URI in `.env`
- For local: `mongod --dbpath C:\data\db`

### Issue: Module Not Found Errors
**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# For spaCy model
python -m spacy download en_core_web_sm
```

### Issue: Import Errors in Python
**Solution:**
```bash
# Add project root to PYTHONPATH
set PYTHONPATH=C:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system
```

### Issue: JWT Token Errors
**Solution:**
- Ensure JWT_SECRET_KEY is set in `.env`
- Check token expiration time
- Generate new token by logging in again

### Issue: File Upload Fails
**Solution:**
- Create uploads directory: `mkdir uploads\resumes`
- Check MAX_CONTENT_LENGTH in config
- Ensure correct Content-Type header

---

## Development Tips

### 1. Enable Debug Mode
In `.env`:
```env
FLASK_DEBUG=True
```

### 2. View Database
Use MongoDB Compass:
- Download: https://www.mongodb.com/products/compass
- Connect to: `mongodb://localhost:27017`

### 3. API Testing Tools
- **Postman**: https://www.postman.com/
- **Insomnia**: https://insomnia.rest/
- **Thunder Client** (VS Code extension)

### 4. Hot Reload
Flask auto-reloads on code changes when DEBUG=True

---

## Next Steps

1. **Frontend Development**
   - Create React app in `frontend/` directory
   - Use Material-UI for components
   - Connect to backend API

2. **LinkedIn Integration**
   - Get LinkedIn API credentials
   - Add OAuth flow
   - Fetch candidate profiles

3. **Email Notifications**
   - Configure SMTP settings
   - Send application confirmations
   - Interview reminders

4. **Deployment**
   - Deploy backend to Heroku/AWS/Azure
   - Use MongoDB Atlas for production
   - Set up CI/CD pipeline

---

## Support

For issues or questions:
- Check API_DOCUMENTATION.md
- Review error logs in console
- Contact project team

---

## Team

- S. Mohana Swarupa (22VV1A0547)
- N. Praneetha (22VV1A0542)
- Y.S.S.D.V.Satya Swaminadh (22VV1A0555)
- Ch. Renuka Sri (22VV1A0509)

**Project Guide**: Mr. R.D.D.V. SIVARAM
