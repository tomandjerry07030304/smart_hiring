# 🚀 Auto-Deployment Setup for Railway

## ✅ AUTOMATIC DEPLOYMENT ENABLED

Railway supports **automatic deployment** from your GitHub repository. Every time you push code, Railway will **automatically rebuild and redeploy** your service.

---

## 🔄 How Auto-Deployment Works

### Current Setup (CLI Deployment)
- You manually run `railway up` to deploy
- Each deployment requires manual trigger

### Auto-Deployment (GitHub Integration)
- **Push to GitHub** → Railway automatically detects changes
- **Auto-builds** using your Dockerfile
- **Auto-deploys** to production
- **Zero manual intervention** required

---

## 📋 Step-by-Step: Enable Auto-Deployment

### Option 1: Connect Existing Railway Project to GitHub (RECOMMENDED)

1. **Push your code to GitHub first:**
```powershell
cd "C:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system"

# Check current remote
git remote -v

# If not already pushed, commit and push
git add aif360-service/
git commit -m "Add AIF360 fairness API service"
git push origin main
```

2. **Link Railway to GitHub:**
```powershell
# Open Railway dashboard
railway open

# In Railway Dashboard:
# → Click on your service "wonderful-luck"
# → Go to "Settings" tab
# → Click "Connect to GitHub"
# → Select repository: my-project-s1
# → Select branch: main
# → Set root directory: /aif360-service
# → Save
```

3. **Configure Build Settings:**
```
Build Path: /aif360-service
Dockerfile Path: Dockerfile
Watch Paths: aif360-service/**
```

4. **Enable Auto-Deploy:**
```
✅ Deploy on Push to main branch
✅ Auto-deploy on PR merge
✅ Deploy on tag creation (optional)
```

---

### Option 2: Fresh GitHub Deployment (Alternative)

If you want to start fresh with GitHub integration:

```powershell
# 1. Initialize Railway with GitHub
cd "C:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system\aif360-service"

# 2. Remove current Railway project link
railway unlink

# 3. Reinitialize with GitHub
railway init --git

# Follow prompts:
# → Connect to GitHub: yes
# → Select repository: SatyaSwaminadhYedida03/my-project-s1
# → Select branch: main
# → Root directory: /aif360-service
# → Auto-deploy: yes

# 4. Initial deployment
railway up
```

---

## ⚙️ Auto-Deployment Configuration

### Configure Deployment Triggers

Edit your `railway.json` to control when deployments happen:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile",
    "watchPatterns": [
      "aif360-service/**"
    ]
  },
  "deploy": {
    "startCommand": "gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT} --timeout 120 --access-logfile - --error-logfile -",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Deployment Triggers (in Railway Dashboard)

You can configure:
- ✅ **Deploy on push to `main`** (default)
- ✅ **Deploy on push to `develop`** (staging)
- ✅ **Deploy on PR merge**
- ✅ **Deploy on Git tag** (for versioned releases)
- ❌ **Manual deployment only** (disable auto-deploy)

---

## 🎯 Workflow After Auto-Deployment is Enabled

### Before (Manual):
```powershell
# Make code changes
code app/main.py

# Manual deployment
railway up
```

### After (Automatic):
```powershell
# 1. Make code changes
code app/main.py

# 2. Commit and push
git add .
git commit -m "Update fairness metrics"
git push origin main

# ✅ Railway automatically detects push
# ✅ Builds Docker image
# ✅ Runs tests (if configured)
# ✅ Deploys to production
# ✅ Sends notification (optional)
```

---

## 📊 Monitoring Auto-Deployments

### View Deployment Status

```powershell
# Check current deployment
railway status

# View deployment logs
railway logs

# Open Railway dashboard
railway open
```

### Railway Dashboard Features:
- **Build Logs**: See Docker build progress
- **Deploy Logs**: View application startup
- **Metrics**: CPU, Memory, Network usage
- **Deployment History**: Track all deployments
- **Rollback**: Instantly revert to previous version

---

## 🔔 Deployment Notifications (Optional)

### Enable Notifications in Railway Dashboard:

1. Go to **Project Settings** → **Notifications**
2. Configure:
   - ✅ **Email notifications** (deployment success/failure)
   - ✅ **Slack integration** (post to #deployments channel)
   - ✅ **Discord webhook** (notify your team)
   - ✅ **GitHub status checks** (show deployment status on PRs)

---

## 🚦 Deployment Strategies

### 1. **Single Branch (Simple)**
```
main branch → Production
```
- Every push to `main` deploys to production
- Best for: Solo projects, MVP development

### 2. **Multi-Branch (Recommended)**
```
develop branch → Staging environment
main branch → Production environment
```

Setup:
```powershell
# Create staging environment
railway environment create staging

# Link staging to develop branch
railway link --environment staging

# Configure in Railway Dashboard:
# Staging: deploy from "develop" branch
# Production: deploy from "main" branch
```

### 3. **Feature Branches (Advanced)**
```
feature/* branches → Preview deployments
develop branch → Staging
main branch → Production
```

- Railway creates **temporary preview URLs** for each PR
- Test features before merging
- Auto-deletes after PR closes

---

## 🛡️ Safety Features

### Pre-Deployment Checks

Add to your GitHub Actions workflow:

```yaml
# .github/workflows/pre-deploy.yml
name: Pre-Deploy Checks

on:
  push:
    branches: [main]
    paths:
      - 'aif360-service/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Tests
        run: |
          cd aif360-service
          pip install -r requirements.txt
          pytest tests/
      
      - name: Lint Code
        run: |
          cd aif360-service
          flake8 app/
      
      - name: Security Scan
        run: |
          cd aif360-service
          bandit -r app/
```

### Rollback Strategy

If deployment fails:

```powershell
# View deployment history
railway deployments

# Rollback to previous version
railway rollback <deployment-id>

# Or use Railway Dashboard:
# → Deployments tab
# → Click "Rollback" on previous successful deployment
```

---

## 📈 Cost Optimization for Auto-Deploy

### Railway Free Tier ($5 credit/month):
- **Build time**: ~10 minutes per deployment
- **Build cost**: ~$0.05 per build
- **Runtime**: ~$0.01 per hour
- **Monthly estimates**:
  - 10 deployments/month = $0.50
  - 24/7 runtime = ~$7.20 (exceeds free tier)
  - **Recommended**: Use for staging, scale up for production

### Cost-Saving Tips:
1. **Sleep inactive services** (auto-sleep after 1 hour idle)
2. **Deploy during off-peak hours** (faster builds)
3. **Use build caching** (faster subsequent builds)
4. **Optimize Docker layers** (reduce build time)

---

## ✅ Verification

### After setting up auto-deployment:

1. **Make a test change:**
```powershell
# Edit a file
echo "# Auto-deploy test" >> aif360-service/README.md

# Commit and push
git add .
git commit -m "Test auto-deployment"
git push origin main
```

2. **Watch Railway Dashboard:**
```powershell
railway open
```

3. **Verify deployment:**
- Railway detects push within 5-10 seconds
- Build starts automatically
- Deployment completes in ~10 minutes
- Health check passes
- Service is live!

4. **Test the API:**
```powershell
# Get your service URL
railway domain

# Test health endpoint
Invoke-RestMethod -Uri "https://YOUR_URL/health"
```

---

## 🎓 Best Practices

### 1. **Use Environment Variables**
Store secrets in Railway dashboard, not in code:
```powershell
railway variables set MONGODB_URI="mongodb+srv://..."
railway variables set SENTRY_DSN="https://..."
```

### 2. **Tag Releases**
Use semantic versioning:
```powershell
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 3. **Monitor Deployments**
Set up alerts for:
- Deployment failures
- High error rates
- Performance degradation

### 4. **Test Before Production**
Always test in staging environment first:
```powershell
# Deploy to staging
git push origin develop

# Test thoroughly
# Then merge to main for production
git checkout main
git merge develop
git push origin main
```

---

## 📞 Support

If auto-deployment isn't working:

1. **Check Railway logs:**
```powershell
railway logs --follow
```

2. **Verify GitHub webhook:**
- Railway Dashboard → Settings → Webhooks
- Should show: ✅ Connected to GitHub

3. **Check repository permissions:**
- Railway needs read/write access to your repo

4. **Contact Railway support:**
- Dashboard → Help & Support
- Or: https://railway.app/help

---

## 🎉 Summary

**Auto-deployment setup:**
1. ✅ Push code to GitHub
2. ✅ Connect Railway to GitHub repo
3. ✅ Configure deployment triggers
4. ✅ Every push auto-deploys

**Benefits:**
- 🚀 **Faster iterations** (push → deploy in 10 min)
- 🔄 **Automatic updates** (no manual intervention)
- 🛡️ **Safer deployments** (with rollback capability)
- 📊 **Better tracking** (deployment history)
- 👥 **Team collaboration** (everyone can deploy)

**Next steps:**
1. Connect to GitHub (see instructions above)
2. Push a test commit
3. Watch auto-deployment happen!
