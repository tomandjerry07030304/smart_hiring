# 🚀 Railway Environment Variables Setup

## CRITICAL: Add PORT Variable to Railway

Railway is using `Dockerfile.aif360` from the root directory, which requires a PORT environment variable.

### Step-by-Step Instructions:

#### 1. Open Railway Dashboard
Go to: https://railway.app/project/fortunate-renewal

#### 2. Navigate to Variables Tab
- Click on your **"web"** service
- Click **"Variables"** tab at the top

#### 3. Add PORT Variable
Click **"New Variable"** and add:

```
Variable Name: PORT
Value: 8000
```

Click **"Add"**

#### 4. The deployment will automatically restart

### Expected Result:

After adding the PORT variable, Railway will:
1. Restart the service automatically
2. The app will bind to port 8000
3. Health check at `/health` will succeed
4. Service status will show **"Active"** ✅

### Verification:

Once deployed, test the endpoint:

```bash
curl https://web-production-3abd8.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Enterprise Fairness Analysis API",
  "version": "2.0.0",
  "aif360_available": true
}
```

---

## Alternative: Railway Auto-Detects PORT

If Railway still fails, it might be because Railway **automatically assigns** a PORT variable but the Dockerfile.aif360 has issues.

### Root Cause Analysis:

The logs show:
```
Using Detected Dockerfile: Dockerfile.aif360
Build: SUCCESS ✅
Deploy: SUCCESS ✅
Healthcheck: FAILED ❌
```

This means:
- ✅ Docker image built correctly
- ✅ Container started
- ❌ App didn't bind to the port Railway expects

### The Issue:

Railway injects `PORT` at runtime but the root `Dockerfile.aif360` had:
```dockerfile
CMD ["sh", "-c", "gunicorn ... --bind 0.0.0.0:${PORT:-8000}"]
```

**Problem**: Shell array syntax doesn't expand `${PORT}` properly!

### The Fix (Already Applied):

Changed to:
```dockerfile
CMD gunicorn app.main:app --bind 0.0.0.0:${PORT:-8000} ...
```

(Without the array brackets, shell expansion works correctly)

---

## Why Railway Uses Root Dockerfile:

Railway is building from the **repository root** even though you set "Root Directory" to `/aif360-service`.

**Reason**: Railway's root directory setting only affects:
- Which directory to CD into before running commands
- Where to look for `railway.json`

But the **Dockerfile path** is still resolved from repo root.

**Solution**: The root `Dockerfile.aif360` now works correctly for Railway deployment.

---

## Summary:

### What Was Fixed:

1. ✅ Removed shell array syntax from CMD
2. ✅ Disabled internal HEALTHCHECK (Railway uses external)
3. ✅ Reduced workers to 1 (memory optimization)
4. ✅ Added proper PORT fallback (${PORT:-8000})

### What You Need to Do:

**Option A**: Add PORT=8000 via Railway dashboard (recommended)
**Option B**: Let Railway auto-assign PORT (should work with current fix)

### Current Status:

- Latest commit: `Fix: Railway PORT handling in root Dockerfile.aif360`
- Pushed to GitHub: ✅
- Railway will auto-deploy in 2-3 minutes

---

## Next Steps:

1. **Wait 3-5 minutes** for Railway to rebuild
2. Check Railway dashboard for **"Active"** status
3. Test health endpoint
4. If still failing, add PORT=8000 manually via dashboard

---

## If It Still Fails:

The nuclear option is to **delete the root Dockerfile.aif360** and force Railway to use the one in `aif360-service/Dockerfile`:

```bash
git mv Dockerfile.aif360 Dockerfile.aif360.backup
git commit -m "Disable root Dockerfile.aif360"
git push origin main
```

Then Railway will auto-detect `aif360-service/Dockerfile` which is already correctly configured.
