# 🚀 Render.com Deployment Guide - Step by Step

## Current Status
✅ Your project is already configured for Render deployment!
- Live URL: https://my-project-smart-hiring.onrender.com
- Repository: SatyaSwaminadhYedida03/my-project-s1

---

## 📋 Pre-Deployment Checklist

### 1. ✅ Files Already Configured
- [x] `Dockerfile` - Production-ready
- [x] `render.yaml` - Render configuration
- [x] `requirements.txt` - Python dependencies
- [x] `app.py` - Main application entry point

### 2. 🔑 Required Environment Variables

You need to set these in Render dashboard:

```bash
# Database (MongoDB Atlas - FREE TIER)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/smart_hiring_db

# Security Keys (Generate new ones!)
SECRET_KEY=<64-character-hex-string>
JWT_SECRET_KEY=<64-character-hex-string>
ENCRYPTION_KEY=<32-byte-base64-string>

# Flask Configuration
FLASK_ENV=production
PORT=8000

# Email (Optional but recommended)
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=Smart Hiring System

# Redis (Optional - for background tasks)
REDIS_URL=redis://red-xxxxx.redis.render.com:6379
```

---

## 🎯 Deployment Steps

### STEP 1: Generate Security Keys

Run these commands in PowerShell:

```powershell
# Generate SECRET_KEY (64 characters)
& "C:/Users/venkat anand/OneDrive/Desktop/4-2/.venv/Scripts/python.exe" -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Generate JWT_SECRET_KEY (64 characters)
& "C:/Users/venkat anand/OneDrive/Desktop/4-2/.venv/Scripts/python.exe" -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"

# Generate ENCRYPTION_KEY (base64)
& "C:/Users/venkat anand/OneDrive/Desktop/4-2/.venv/Scripts/python.exe" -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

**SAVE THESE KEYS!** You'll need them in Step 5.

---

### STEP 2: Setup MongoDB Atlas (FREE)

1. **Go to**: https://www.mongodb.com/cloud/atlas/register
2. **Create free account**
3. **Create cluster**: 
   - Select FREE tier (M0)
   - Choose region closest to you
4. **Create database user**:
   - Database Access → Add New User
   - Username: `smarthiring`
   - Password: Generate secure password
5. **Whitelist all IPs**:
   - Network Access → Add IP Address
   - Enter: `0.0.0.0/0` (Allow from anywhere)
6. **Get connection string**:
   - Click "Connect" → "Connect your application"
   - Copy connection string
   - Replace `<password>` with your password
   - Replace `<dbname>` with `smart_hiring_db`

**Example**:
```
mongodb+srv://smarthiring:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/smart_hiring_db?retryWrites=true&w=majority
```

---

### STEP 3: Push to GitHub

```powershell
# Navigate to project
Set-Location "C:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system"

# Check status
git status

# Add all files (if needed)
git add .

# Commit changes
git commit -m "Deploy: Ready for Render.com deployment"

# Push to main branch
git push origin main
```

---

### STEP 4: Connect Render to GitHub

1. **Go to**: https://dashboard.render.com/
2. **Login/Sign up** with GitHub
3. **New → Web Service**
4. **Connect repository**: `SatyaSwaminadhYedida03/my-project-s1`
5. **Grant access** to the repository

---

### STEP 5: Configure Web Service

**Basic Settings**:
- **Name**: `smart-hiring-system` (or any name you want)
- **Region**: Choose closest region (e.g., Oregon, Singapore)
- **Branch**: `main`
- **Runtime**: `Docker`
- **Dockerfile Path**: `./Dockerfile`
- **Instance Type**: `Free` (or Starter $7/month for better performance)

**Environment Variables** (Click "Add Environment Variable"):

Add each of these:

```
MONGODB_URI = mongodb+srv://smarthiring:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/smart_hiring_db
SECRET_KEY = <paste from Step 1>
JWT_SECRET_KEY = <paste from Step 1>
ENCRYPTION_KEY = <paste from Step 1>
FLASK_ENV = production
PORT = 8000
JWT_ACCESS_TOKEN_EXPIRES = 3600
EMAIL_ENABLED = false
```

**Advanced Settings**:
- **Auto-Deploy**: Yes (deploys on every git push)
- **Health Check Path**: `/health`

---

### STEP 6: Deploy!

1. Click **"Create Web Service"**
2. **Wait 5-10 minutes** for initial build
3. Watch the logs in real-time
4. When you see "Service is live 🎉", deployment is complete!

---

## 🔍 Verify Deployment

### Check Health Endpoint
```bash
curl https://your-app-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-07T...",
  "checks": {
    "database": true,
    "redis": false
  }
}
```

### Test Registration
Visit: `https://your-app-name.onrender.com`

Try creating an account!

---

## 🐛 Troubleshooting

### Issue: Build Failed

**Check logs for**:
- Missing dependencies → Update `requirements.txt`
- Python version mismatch → Check `Dockerfile`
- File not found → Verify file paths in `Dockerfile`

**Solution**:
```powershell
# Fix issues locally, then:
git add .
git commit -m "Fix: Build errors"
git push origin main
# Render will auto-redeploy
```

### Issue: MongoDB Connection Failed

**Symptoms**: 
```
pymongo.errors.ServerSelectionTimeoutError
```

**Solutions**:
1. ✅ Check MongoDB IP whitelist: `0.0.0.0/0`
2. ✅ Verify connection string format
3. ✅ Ensure password doesn't have special characters (use alphanumeric)
4. ✅ Test connection locally first

### Issue: SECRET_KEY Error

**Error**:
```
ValueError: SECRET_KEY must be set and at least 32 characters long
```

**Solution**:
- Verify `SECRET_KEY` is set in Render dashboard
- Must be 64 characters (32 bytes hex)
- Regenerate using Step 1 command

### Issue: App Crashes After Deploy

**Check**:
1. View logs in Render dashboard
2. Look for Python errors
3. Check environment variables are set correctly

**Common fixes**:
```bash
# Missing dependency
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

---

## 📊 Post-Deployment

### Monitor Your App

**Render Dashboard**:
- **Logs**: Real-time application logs
- **Metrics**: CPU, Memory, Response time
- **Events**: Deployment history

**Health Check**:
```bash
# Check every 5 minutes
curl https://your-app-name.onrender.com/health
```

### Update Environment Variables

1. Go to Render Dashboard
2. Click your service
3. Navigate to "Environment"
4. Update variables
5. Click "Save Changes"
6. App will automatically restart

---

## 🎉 Your App is Live!

**Access your app**:
```
https://your-app-name.onrender.com
```

**API endpoints**:
```
https://your-app-name.onrender.com/api/auth/register
https://your-app-name.onrender.com/api/jobs/list
https://your-app-name.onrender.com/api/auth/login
```

**Share with faculty**:
```
Project Demo: https://your-app-name.onrender.com
API Docs: https://your-app-name.onrender.com/api/docs
```

---

## 🔄 Continuous Deployment

After initial setup, deploying updates is automatic:

```powershell
# Make changes to code
# ...

# Commit and push
git add .
git commit -m "Feature: Added new functionality"
git push origin main

# Render automatically detects push and redeploys!
# Check deployment status in dashboard
```

---

## 💰 Pricing

**Free Tier** (Current):
- ✅ 750 hours/month (enough for 24/7 uptime)
- ✅ Auto-sleeps after 15 min inactivity
- ✅ Wakes up on first request (~30 seconds)
- ✅ Perfect for demos and faculty review

**Starter Tier** ($7/month):
- Always on (no sleep)
- Faster performance
- Custom domain support

---

## 📞 Support

**Render Documentation**: https://render.com/docs
**MongoDB Atlas Docs**: https://docs.atlas.mongodb.com/

**Need help?**
- Check Render logs first
- Review error messages
- Test locally before deploying

---

## ✅ Deployment Complete Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Database user created with password
- [ ] IP whitelist set to `0.0.0.0/0`
- [ ] Connection string copied
- [ ] Security keys generated (SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY)
- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] Environment variables set in Render
- [ ] Deployment successful
- [ ] Health check returns 200 OK
- [ ] Can register/login successfully
- [ ] Shared URL with faculty

**When all checked, your project is LIVE! 🚀**
