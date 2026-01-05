# 🚂 Railway Deployment Guide - Smart Hiring System

## Why Railway?
- ✅ **No slug size limits** (unlike Render's 512MB)
- ✅ **Full ML/AI support** - pandas, scikit-learn, spacy all work
- ✅ **Free tier** - 500 hours/month ($5 credit)
- ✅ **Native Docker** - Full control
- ✅ **Easy environment variables**
- ✅ **Auto-deploys from GitHub**

---

## 🚀 Quick Deployment (5 Minutes)

### Step 1: Install Railway CLI
```powershell
npm install -g @railway/cli
```

### Step 2: Login to Railway
```powershell
railway login
```

### Step 3: Initialize Project
```powershell
cd "c:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system"
railway init
```
Select: **Empty Project** → Name: `smart-hiring-system`

### Step 4: Set Environment Variables
```powershell
railway variables set MONGODB_URI="your-mongodb-atlas-connection-string"
railway variables set JWT_SECRET_KEY="your-super-secret-jwt-key-min-32-chars"
railway variables set SECRET_KEY="your-flask-secret-key"
railway variables set FLASK_ENV="production"
railway variables set PORT="8000"
```

### Step 5: Deploy!
```powershell
railway up
```

### Step 6: Get Your URL
```powershell
railway domain
```
This gives you a URL like: `smart-hiring-system.up.railway.app`

---

## 📋 Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster.mongodb.net/smart_hiring_db` |
| `JWT_SECRET_KEY` | JWT signing key (32+ chars) | `your-super-secret-jwt-key-change-this` |
| `SECRET_KEY` | Flask secret key | `another-secret-key-for-flask` |
| `FLASK_ENV` | Environment | `production` |
| `PORT` | Port (Railway sets this) | `8000` |

### Optional Variables:
| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection | (disabled if not set) |
| `SENTRY_DSN` | Error tracking | (disabled if not set) |
| `ALLOWED_ORIGINS` | CORS origins | `*` |

---

## 🗄️ MongoDB Atlas Setup (Free)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create free cluster (M0 - Free Forever)
3. Create database user
4. Whitelist IP: `0.0.0.0/0` (allow all for cloud)
5. Get connection string → Use in `MONGODB_URI`

---

## 🔄 Auto-Deploy from GitHub

### Option A: Railway Dashboard
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. New Project → Deploy from GitHub
3. Select your repository
4. Railway auto-detects Dockerfile

### Option B: CLI with GitHub
```powershell
railway link  # Link to existing project
git push      # Triggers auto-deploy
```

---

## 📊 Features Enabled on Railway

| Feature | Status |
|---------|--------|
| ✅ Authentication | Full |
| ✅ Job Management | Full |
| ✅ Candidate Management | Full |
| ✅ **Assessment System** | **ENABLED** (scikit-learn works!) |
| ✅ **Dashboard Analytics** | **ENABLED** (pandas works!) |
| ✅ **PDF/DOCX Resume Parsing** | **ENABLED** |
| ✅ **ML Matching** | **ENABLED** |
| ✅ **Fairness Engine** | **ENABLED** |

---

## 🧪 Test Deployment

After deploying, test these endpoints:

```powershell
# Health check
curl https://your-app.up.railway.app/api/health

# Test login (after creating accounts)
curl -X POST https://your-app.up.railway.app/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"admin@smarthiring.com","password":"Admin@123"}'
```

---

## 💰 Railway Pricing

### Free Tier (Starter):
- $5 free credit/month
- ~500 hours runtime
- 512MB RAM, 1GB disk
- **Perfect for demo/development**

### Pro ($20/month):
- 8GB RAM, 100GB disk
- Custom domains
- Team features

---

## 🔧 Troubleshooting

### Build Fails?
```powershell
railway logs  # Check build logs
```

### App Crashes?
```powershell
railway logs --tail 100  # Live logs
```

### Need More Memory?
Upgrade to Pro or optimize Dockerfile.

---

## 📁 Files for Railway

Your project already has:
- ✅ `Dockerfile` - Container build
- ✅ `railway.json` - Railway config
- ✅ `requirements.txt` - Dependencies
- ✅ `.railwayignore` - Exclude files

---

## 🎯 Quick Commands Reference

```powershell
railway login          # Authenticate
railway init           # New project
railway up             # Deploy
railway logs           # View logs
railway domain         # Get/set domain
railway variables      # Manage env vars
railway open           # Open dashboard
railway down           # Stop service
```

---

## ✅ Post-Deployment Checklist

1. [ ] Set all environment variables
2. [ ] Test health endpoint
3. [ ] Create test accounts (run setup_test_accounts.py locally)
4. [ ] Test login from all portals
5. [ ] Test job creation
6. [ ] Test application submission
7. [ ] Verify ML features work (matching scores)

---

**Need Help?** Railway Discord: https://discord.gg/railway
