
# 🚂 Railway Deployment - Quick Start Guide

## Complete Railway Deployment (10 Minutes)

### Prerequisites
- ✅ Railway account (free): https://railway.app/
- ✅ npm installed (for Railway CLI)
- ✅ Git initialized in project

---

## 📋 Step-by-Step Commands

### 1. Install Railway CLI

```powershell
# Install via npm
npm install -g @railway/cli

# Verify
railway version
```

**Expected output:**
```
railway version 3.x.x
```

---

### 2. Login to Railway

```powershell
railway login
```

**What happens:**
1. Opens browser automatically
2. Click "Authorize" on Railway website
3. Terminal shows: ✅ "Logged in as your-email@example.com"

---

### 3. Navigate to Project

```powershell
cd "C:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system\aif360-service"
```

---

### 4. Initialize Railway Project

```powershell
railway init
```

**Interactive prompts:**
```
? Create a new Project or link to an existing one?
→ Create new Project

? Project name
→ aif360-fairness-api (or your preferred name)

? Environment
→ production

✅ Project created successfully
```

---

### 5. Link to GitHub (Optional but Recommended)

```powershell
# If you have GitHub repo
railway link

# Or deploy directly without GitHub
# (skip this step, use railway up instead)
```

---

### 6. Set Environment Variables (Optional)

```powershell
# Set variables via CLI
railway variables set LOG_LEVEL=info
railway variables set WORKERS=2

# Or set in Railway dashboard (easier)
```

---

### 7. Deploy Application

```powershell
# Deploy (uses Dockerfile automatically)
railway up

# ✅ Railway detects Dockerfile
# ✅ Builds image with system packages
# ✅ Installs AIF360
# ✅ Starts service
```

**Expected output:**
```
🚝 Building...
  → Detected Dockerfile
  → Installing system dependencies (gcc, gfortran, libblas, liblapack)
  → Installing Python packages
  → Installing aif360==0.6.1
  ✅ Build successful (8m 32s)

🚀 Deploying...
  ✅ Deployment successful

🌐 Service URL: https://aif360-fairness-api-production.up.railway.app
```

---

### 8. Generate Public URL

```powershell
# Generate public domain
railway domain

# Your API will be available at:
# https://YOUR_PROJECT.up.railway.app
```

---

### 9. View Logs

```powershell
# Stream logs in real-time
railway logs

# Or view in Railway dashboard
railway open
```

---

### 10. Test Deployment

```powershell
# Save your Railway URL
$RAILWAY_URL = "https://YOUR_PROJECT.up.railway.app"

# Test health check
Invoke-RestMethod -Uri "$RAILWAY_URL/health"

# Expected response:
# {
#   "status": "healthy",
#   "aif360_available": true,
#   "timestamp": "2025-12-05T..."
# }
```

---

## 🧪 Test Fairness Analysis

```powershell
# Create test payload
$payload = @'
{
  "applications": [
    {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
    {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
    {"protected_attribute": "male", "decision": 1, "ground_truth": 0},
    {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
    {"protected_attribute": "male", "decision": 1, "ground_truth": 0},
    {"protected_attribute": "female", "decision": 0, "ground_truth": 1},
    {"protected_attribute": "female", "decision": 0, "ground_truth": 1},
    {"protected_attribute": "female", "decision": 0, "ground_truth": 0},
    {"protected_attribute": "female", "decision": 0, "ground_truth": 1},
    {"protected_attribute": "female", "decision": 0, "ground_truth": 0}
  ],
  "protected_attribute_name": "gender"
}
'@

# Test analysis endpoint
Invoke-RestMethod -Uri "$RAILWAY_URL/analyze" `
  -Method POST `
  -ContentType "application/json" `
  -Body $payload | ConvertTo-Json -Depth 10
```

**Expected response:**
```json
{
  "bias_detected": true,
  "fairness_badge": {
    "grade": "F",
    "score": 12.5,
    "level": "Critical Bias"
  },
  "fairness_metrics": {
    "statistical_parity_difference": 1.0,
    "disparate_impact_ratio": 0.0
  },
  "violations": [...],
  "recommendations": [...]
}
```

---

## 📊 Railway Dashboard

### Access Dashboard

```powershell
# Open Railway dashboard in browser
railway open
```

**In the dashboard you can:**
- 📈 View metrics (CPU, memory, requests)
- 📝 View logs in real-time
- ⚙️ Configure environment variables
- 🔗 Manage domains
- 💳 Check usage and billing

---

## 💰 Cost Tracking

### Free Tier Details

**Railway Free Tier:**
- 💵 **$5 credit per month**
- ⏰ **No time limit** (credit-based)
- 📦 **500MB RAM** per service
- 🚀 **No cold starts**

**Estimated Usage:**
```
Build time: ~$0.01 per deploy
Runtime: ~$0.01 per hour

$5 credit = ~500 hours/month
           = ~16 hours/day
           = Perfect for development/demo
```

### Check Usage

```powershell
# View current usage
railway status

# Or check in dashboard
railway open
# → Navigate to "Usage" tab
```

---

## 🔄 Redeploy After Changes

### Method 1: CLI Redeploy

```powershell
# After making code changes
railway up

# Railway rebuilds and redeploys automatically
```

### Method 2: GitHub Auto-Deploy

```powershell
# 1. Push to GitHub
git add .
git commit -m "Update API"
git push origin main

# 2. Railway auto-deploys (if linked to GitHub)
# ✅ Automatic deployment triggered
```

---

## ⚙️ Environment Variables

### Set via CLI

```powershell
# Single variable
railway variables set KEY=value

# Multiple variables
railway variables set LOG_LEVEL=info WORKERS=2 PORT=8000
```

### Set via Dashboard

1. `railway open`
2. Click "Variables" tab
3. Add key-value pairs
4. Click "Deploy" to apply

**Recommended variables:**
```
LOG_LEVEL=info
WORKERS=2
PORT=8000
PYTHONUNBUFFERED=1
```

---

## 🐛 Troubleshooting

### Issue: Build fails with "out of memory"

**Solution:**
```powershell
# Upgrade to Railway Pro ($5/month)
# Or reduce dependencies in requirements.txt
```

### Issue: Service not responding

**Check logs:**
```powershell
railway logs --tail 100
```

**Common causes:**
- Port mismatch (Railway injects $PORT)
- Health check failing
- Application crash on startup

**Fix:**
Ensure Dockerfile CMD uses `$PORT`:
```dockerfile
CMD ["sh", "-c", "gunicorn app.main:app --bind 0.0.0.0:${PORT}"]
```

### Issue: AIF360 import error

**Check build logs:**
```powershell
railway logs --deployment [DEPLOYMENT_ID]
```

**Ensure Dockerfile installs system packages:**
```dockerfile
RUN apt-get update && apt-get install -y gcc g++ gfortran libblas-dev liblapack-dev
```

---

## 📈 Monitoring

### View Metrics

```powershell
# Open dashboard
railway open

# View:
# - Request count
# - Response times
# - Error rates
# - Memory usage
# - CPU usage
```

### Set Up Alerts (Railway Pro)

1. Navigate to "Observability"
2. Configure alerts for:
   - High error rate
   - Memory usage > 80%
   - Deployment failures

---

## 🔐 Security

### Enable HTTPS (Automatic)

Railway provides **automatic HTTPS** on all custom domains.

**Your API is secure by default:**
```
https://your-project.up.railway.app
```

### Add Custom Domain

```powershell
# Via CLI
railway domain add yourdomain.com

# Or in dashboard:
# 1. railway open
# 2. Settings → Domains
# 3. Add custom domain
# 4. Update DNS records (Railway provides instructions)
```

---

## 🎯 Integration with Smart Hiring System

### Update Your Main App

**In `backend/config.py` or environment variables:**

```python
# Add Railway API URL
FAIRNESS_API_URL = "https://your-railway-url.up.railway.app"
```

**In `backend/routes/company_routes.py`:**

```python
import requests

@company_bp.route('/api/company/jobs/<job_id>/fairness-report', methods=['POST'])
def generate_fairness_report(job_id):
    # Get applications
    applications = get_applications_for_job(job_id)
    
    # Call Railway-hosted AIF360 API
    response = requests.post(
        f"{FAIRNESS_API_URL}/analyze",
        json={
            "applications": applications,
            "protected_attribute_name": "gender"
        }
    )
    
    return jsonify(response.json())
```

---

## 📋 Deployment Checklist

Before going live:

- [ ] Railway CLI installed
- [ ] Logged into Railway
- [ ] Project initialized (`railway init`)
- [ ] Environment variables set
- [ ] Application deployed (`railway up`)
- [ ] Public domain generated (`railway domain`)
- [ ] Health check tested (`/health` endpoint)
- [ ] Fairness analysis tested (`/analyze` endpoint)
- [ ] Logs reviewed (no errors)
- [ ] Usage tracked (within free tier)
- [ ] Main app integrated (API calls work)

---

## 🚀 Advanced Features

### Database Integration

```powershell
# Add PostgreSQL
railway add postgres

# Get connection string
railway variables

# Use in your app
# DATABASE_URL will be automatically set
```

### Redis Caching

```powershell
# Add Redis
railway add redis

# Use for caching fairness results
```

### Multiple Environments

```powershell
# Create staging environment
railway environment create staging

# Deploy to staging
railway up --environment staging

# Deploy to production
railway up --environment production
```

---

## 💡 Pro Tips

1. **Use `railway logs --tail 100`** frequently during development
2. **Enable GitHub auto-deploy** for continuous deployment
3. **Monitor usage** to avoid running out of free credits
4. **Use Railway dashboard** for easier variable management
5. **Set up Slack/Discord webhooks** for deployment notifications

---

## 📚 Resources

- **Railway Documentation:** https://docs.railway.app/
- **Railway CLI:** https://docs.railway.app/develop/cli
- **AIF360 Documentation:** https://aif360.readthedocs.io/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/

---

## 🎉 Success!

Your AIF360 Fairness API is now live on Railway!

**Your API URL:**
```
https://your-project.up.railway.app
```

**API Documentation:**
```
https://your-project.up.railway.app/docs
```

**Test it:**
```powershell
curl https://your-project.up.railway.app/health
```

---

## 📞 Need Help?

- **Railway Support:** https://railway.app/discord
- **GitHub Issues:** Create issue in your repo
- **Documentation:** Refer to DEPLOYMENT_GUIDE.md

---

**Deployment Time:** ~10 minutes  
**Cost:** $0 (uses free $5 credit)  
**Status:** ✅ Production Ready  
**Platform:** Railway.app

**Happy deploying! 🚂🚀**
