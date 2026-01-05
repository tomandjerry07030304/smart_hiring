# 🚨 Render Deployment Issue - Complete Fix Guide

## Current Status (from Screenshots)

Your Smart Hiring System is deployed at: `my-project-smart-hiring.onrender.com`

### ✅ Working Features:
- Authentication System - **Active**
- Job Management - **Active**
- Candidate Management - **Active**

### ⚠️ Disabled Features (Due to 512MB Slug Limit):
- Assessment System - **DISABLED** (scikit-learn removed)
- Dashboard Analytics - **DISABLED** (pandas removed)
- PDF/DOCX Resume Parsing - **DISABLED** (PyPDF2/python-docx removed)
- Quick Stats showing "--" instead of values

---

## 🔧 SOLUTION OPTIONS

### Option A: Upgrade Render Plan (Fastest - $7/month)
1. Go to: https://dashboard.render.com
2. Click on your web service
3. Go to **Settings** → **Plan**
4. Upgrade to **Starter** plan
5. Redeploy with full requirements.txt

### Option B: Use Split Architecture (FREE - Recommended)

Deploy heavy ML operations as a separate microservice on Railway.app (free tier).

#### Already Created Files:
- `ml-service/app.py` - ML microservice with endpoints
- `ml-service/requirements.txt` - ML dependencies
- `ml-service/Dockerfile` - Container config
- `ml-service/railway.json` - Railway deployment config

---

## 📦 Deploy ML Microservice to Railway (FREE)

### Step 1: Install Railway CLI
```powershell
npm install -g @railway/cli
```

### Step 2: Login to Railway
```powershell
cd c:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system\ml-service
railway login
```

### Step 3: Create New Project
```powershell
railway init
# Select: "Empty Project"
# Name: "smart-hiring-ml"
```

### Step 4: Deploy
```powershell
railway up
```

### Step 5: Get the Public URL
```powershell
railway domain
# This will give you something like: smart-hiring-ml.up.railway.app
```

---

## 🔗 Update Render Environment Variables

After deploying ML microservice, add these to Render:

| Variable | Value |
|----------|-------|
| `ML_SERVICE_URL` | `https://smart-hiring-ml.up.railway.app` |
| `ML_SERVICE_SECRET` | `your-secret-key-here` |

---

## 🧪 Test the ML Microservice

Once deployed, test these endpoints:

```powershell
# Health Check
curl https://smart-hiring-ml.up.railway.app/health

# Extract Skills
curl -X POST https://smart-hiring-ml.up.railway.app/api/extract-skills `
  -H "Content-Type: application/json" `
  -d '{"text": "Python developer with 5 years of experience in Django and React"}'

# Calculate Match Score
curl -X POST https://smart-hiring-ml.up.railway.app/api/calculate-match `
  -H "Content-Type: application/json" `
  -d '{
    "job_description": "Looking for Python developer",
    "resume_text": "5 years Python experience",
    "job_skills": ["python", "django"],
    "candidate_skills": ["python", "flask"]
  }'
```

---

## 📋 Quick Stats Fix

The "--" values in Quick Stats mean the analytics endpoint is returning empty data.

### Immediate Fix (Local Testing):
```powershell
cd c:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system
python backend/app.py
```

Then visit: http://localhost:5000

### Fix for Render:
The Quick Stats should work after:
1. Either upgrading Render plan, OR
2. Connecting to ML microservice for analytics

---

## 🔒 Login Page Troubleshooting

If login is not working on Render:

### Check 1: API URL Configuration
The frontend auto-detects API URL:
```javascript
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000/api'
    : window.location.origin + '/api';
```

### Check 2: MongoDB Connection
Ensure Render has correct MongoDB environment variable:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/smart_hiring_db
```

### Check 3: JWT Secret
Ensure `JWT_SECRET_KEY` is set in Render environment variables.

### Check 4: CORS Configuration
The backend should allow your Render domain.

---

## 🚀 Complete Environment Variables for Render

```env
# Database
MONGODB_URI=your_mongodb_atlas_uri

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
SECRET_KEY=your-flask-secret-key

# ML Microservice (after deploying to Railway)
ML_SERVICE_URL=https://smart-hiring-ml.up.railway.app
ML_SERVICE_SECRET=your-ml-service-secret

# Flask
FLASK_ENV=production
PORT=5000

# Features (with microservice)
ENABLE_ASSESSMENTS=true
ENABLE_ANALYTICS=true
ENABLE_RESUME_PARSING=true
```

---

## 📊 Architecture After Fix

```
┌─────────────────────────────────────────────────────┐
│                    USERS                            │
│              (Browser/Mobile)                       │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              Render.com (FREE)                      │
│         my-project-smart-hiring.onrender.com        │
│                                                     │
│  • Flask Backend (lightweight)                      │
│  • Authentication                                   │
│  • Job Management                                   │
│  • Candidate Management                             │
│  • API Gateway                                      │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              Railway.app (FREE)                     │
│         smart-hiring-ml.up.railway.app              │
│                                                     │
│  • Resume Parsing (PDF/DOCX)                        │
│  • Skill Extraction                                 │
│  • Match Scoring (TF-IDF)                           │
│  • Analytics (pandas)                               │
│  • Fairness Metrics                                 │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              MongoDB Atlas (FREE)                   │
│                                                     │
│  • Users, Jobs, Applications                        │
│  • Assessments, Results                             │
└─────────────────────────────────────────────────────┘
```

---

## ⏱️ Time Estimates

| Solution | Time | Cost |
|----------|------|------|
| Upgrade Render | 5 minutes | $7/month |
| Deploy ML Microservice | 30 minutes | FREE |

---

## Need Help?

If login still doesn't work after checking the above:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Try logging in
4. Look for red requests (errors)
5. Share the error details

The most common issues are:
- MongoDB connection string incorrect
- JWT_SECRET_KEY not set
- CORS not configured for production domain
