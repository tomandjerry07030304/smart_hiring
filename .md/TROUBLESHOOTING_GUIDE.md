# ============================================================================
# DOCKER ENVIRONMENT VARIABLE TROUBLESHOOTING GUIDE
# ============================================================================
# Complete forensic analysis and step-by-step debugging for:
# "ValueError: SECRET_KEY must be set and at least 32 characters long"
# ============================================================================

## 🔥 CRITICAL FINDINGS - ROOT CAUSE ANALYSIS

### PRIMARY ISSUE #1: `.env` BLOCKED BY `.dockerignore`

**Problem:**
Your `.dockerignore` file (lines 32-34) contains:
```
.env
.env.local
.env.production
```

**Impact:**
- Docker **CANNOT SEE** your `.env` file during build
- Environment variables are **NOT AVAILABLE** at runtime
- `SECRET_KEY` validation **ALWAYS FAILS**

**Solution:**
```bash
# Option 1: Use the fixed .dockerignore
cp .dockerignore.fixed .dockerignore

# Option 2: Comment out .env line manually
# Edit .dockerignore and add # before .env:
# # .env
# # .env.local  
# # .env.production
```

---

### PRIMARY ISSUE #2: CONFIG VALIDATION TOO EARLY

**Problem:**
`config/config.py` (lines 8-15) validates **IMMEDIATELY** on import:

```python
load_dotenv()  # Tries to load .env
SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError('SECRET_KEY must be set and at least 32 characters long')
```

**Impact:**
- Validation happens **BEFORE** docker-compose injects env vars
- If `.env` is blocked, `SECRET_KEY` is `None`
- Application **CRASHES** on startup

**Solution:**
Use the new config system with lazy loading:
```python
# Replace old config import:
# from config.config import config

# With new config import:
from config.config_v2_fixed import get_config
config = get_config()
```

---

### PRIMARY ISSUE #3: WEAK SECRET IN `.env`

**Problem:**
Your `.env` file contains:
```
SECRET_KEY=your-flask-secret-key  # Only 22 characters!
```

**Impact:**
- Fails validation (< 32 characters)
- Not cryptographically secure
- Production vulnerability

**Solution:**
Generate a strong 64-character secret:

```bash
# PowerShell:
python -c "import secrets; print(secrets.token_hex(32))"

# Output example:
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

Update `.env`:
```ini
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
JWT_SECRET_KEY=f2e1d0c9b8a7z6y5x4w3v2u1t0s9r8q7p6o5n4m3l2k1j0i9h8g7f6e5d4c3b2a1
```

---

### PRIMARY ISSUE #4: NO `env_file:` IN `docker-compose.yml`

**Problem:**
Your `docker-compose.yml` relies on shell environment variables:
```yaml
environment:
  SECRET_KEY: ${SECRET_KEY:-changeme_replace_with_secure_random}
```

But has NO `env_file:` directive to load `.env`

**Impact:**
- Docker doesn't load `.env` automatically
- Falls back to weak default `changeme_replace_with_secure_random`
- Default is 34 chars (barely passes but insecure)

**Solution:**
Use `docker-compose.fixed.yml` which includes:
```yaml
env_file:
  - ../.env

environment:
  SECRET_KEY: ${SECRET_KEY}
```

---

## 🔍 STEP-BY-STEP DEBUGGING PROCEDURE

### Step 1: Verify `.env` File Exists and Contains Valid Secrets

```powershell
# Check if .env exists
Test-Path .env

# View SECRET_KEY (be careful - this exposes secrets!)
Select-String -Path .env -Pattern "SECRET_KEY"

# Check length
$secretKey = (Select-String -Path .env -Pattern "^SECRET_KEY=(.+)").Matches.Groups[1].Value
Write-Host "SECRET_KEY length: $($secretKey.Length) characters"

# Must be >= 32 characters
```

**Expected Output:**
```
True
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
SECRET_KEY length: 66 characters
```

---

### Step 2: Verify `.dockerignore` Does NOT Block `.env`

```powershell
# Check .dockerignore content
Get-Content .dockerignore | Select-String -Pattern "^\.env"

# Should return NOTHING or commented lines only
```

**Expected Output:**
```
(blank - no matches)
```

**If you see:**
```
.env
.env.local
```

**Fix:**
```powershell
# Use fixed version
cp .dockerignore.fixed .dockerignore
```

---

### Step 3: Clean Docker Environment Completely

```powershell
# Stop all containers
docker compose -f deploy/docker-compose.yml down -v

# Remove all stopped containers
docker container prune -f

# Remove all images
docker image prune -af

# Remove all volumes
docker volume prune -f

# Verify nothing is running
docker ps -a
```

---

### Step 4: Build with Fixed Configuration

```powershell
# Navigate to project root
cd "c:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system"

# Build with fixed docker-compose
docker compose -f deploy/docker-compose.fixed.yml build --no-cache --progress=plain
```

**Watch for errors during build. Expected:**
```
[+] Building 120.5s (15/15) FINISHED
 => [backend] exporting to image
 => => naming to docker.io/library/smart-hiring-backend:latest
```

---

### Step 5: Start Containers

```powershell
# Start all services
docker compose -f deploy/docker-compose.fixed.yml up -d --force-recreate

# Wait 10 seconds
Start-Sleep -Seconds 10

# Check status
docker compose -f deploy/docker-compose.fixed.yml ps
```

**Expected Output:**
```
NAME                    STATUS    PORTS
smart_hiring_backend    Up        0.0.0.0:8000->8000/tcp
smart_hiring_mongodb    Up        0.0.0.0:27017->27017/tcp
smart_hiring_redis      Up        0.0.0.0:6379->6379/tcp
smart_hiring_worker     Up        (no ports)
```

---

### Step 6: Check Environment Variables Inside Container

```powershell
# Check SECRET_KEY inside backend container
docker exec -it smart_hiring_backend printenv | Select-String -Pattern "SECRET"

# Check all critical env vars
docker exec -it smart_hiring_backend printenv | Select-String -Pattern "(SECRET|JWT|MONGO|REDIS)"
```

**Expected Output:**
```
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
JWT_SECRET_KEY=f2e1d0c9b8a7z6y5x4w3v2u1t0s9r8q7p6o5n4m3l2k1j0i9h8g7f6e5d4c3b2a1
MONGODB_URI=mongodb://admin:***@mongodb:27017/smart_hiring_db?authSource=admin
REDIS_URL=redis://:***@redis:6379/0
```

**If SECRET_KEY is missing or wrong:**
- `.env` file is not being loaded
- Check `env_file:` in docker-compose.yml
- Verify path to `.env` is correct (relative to docker-compose.yml location)

---

### Step 7: Test Config Loading Inside Container

```powershell
# Test new config system
docker exec -it smart_hiring_backend python -c "from config.config_v2_fixed import get_config; c = get_config(); print(c.get_summary())"
```

**Expected Output:**
```json
{
  'app_name': 'SmartHiringSystem',
  'environment': 'production',
  'port': 8000,
  'secret_key_length': 66,
  'jwt_expiry': 3600
}
```

**If you see errors:**
```
ValidationError: SECRET_KEY must be set and at least 32 characters long
```

Then environment variables are NOT reaching the Python app.

---

### Step 8: Check Backend Logs

```powershell
# View last 100 lines of backend logs
docker logs smart_hiring_backend --tail=100

# Follow logs in real-time
docker logs smart_hiring_backend -f
```

**Look for:**

✅ **SUCCESS:**
```
✅ Configuration loaded successfully
🚀 Starting Smart Hiring System
🌐 Listening on http://0.0.0.0:8000
```

❌ **FAILURE:**
```
ValueError: SECRET_KEY must be set and at least 32 characters long
Traceback (most recent call last):
  File "/app/config/config.py", line 13, in <module>
```

---

### Step 9: Test Backend Health Endpoint

```powershell
# Test from host machine
curl http://localhost:8000/api/health

# Or using PowerShell
Invoke-WebRequest -Uri http://localhost:8000/api/health -UseBasicParsing
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-07T...",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

---

## 🚨 COMMON ERROR SCENARIOS

### Scenario 1: "SECRET_KEY must be set" on Container Startup

**Symptom:**
```
docker logs smart_hiring_backend
ValueError: SECRET_KEY must be set and at least 32 characters long
```

**Root Cause:**
- `.env` blocked by `.dockerignore`
- No `env_file:` in docker-compose
- Config validates too early

**Fix:**
1. Use `.dockerignore.fixed`
2. Use `docker-compose.fixed.yml`
3. Use `config_v2_fixed.py`

---

### Scenario 2: SECRET_KEY Exists But Still Fails

**Symptom:**
```powershell
docker exec -it smart_hiring_backend printenv | grep SECRET
SECRET_KEY=a1b2c3d4...
# But app still crashes
```

**Root Cause:**
- Old config cached in Python `__pycache__`
- Import happens before env loaded

**Fix:**
```powershell
# Rebuild with no cache
docker compose -f deploy/docker-compose.fixed.yml build --no-cache

# Remove pycache inside container
docker exec -it smart_hiring_backend find /app -name "__pycache__" -type d -exec rm -rf {} +
```

---

### Scenario 3: Works Locally But Not in Docker

**Root Cause Table:**

| Aspect | Local | Docker |
|--------|-------|--------|
| `.env` location | Project root | Blocked by `.dockerignore` |
| Working directory | Variable | Always `/app` |
| Config import | After dotenv | During build (too early) |
| Env var source | `.env` file | `environment:` in compose |

**Fix:**
Use `docker-compose.fixed.yml` with proper `env_file:` directive.

---

### Scenario 4: Backend Starts, Worker Crashes

**Symptom:**
```powershell
docker logs smart_hiring_worker
ValueError: SECRET_KEY must be set
```

**Root Cause:**
Worker container missing `env_file:` directive.

**Fix:**
`docker-compose.fixed.yml` includes identical env vars for worker:
```yaml
worker:
  env_file:
    - ../.env
  environment:
    SECRET_KEY: ${SECRET_KEY}
    # ... (same as backend)
```

---

## ✅ FINAL VERIFICATION CHECKLIST

After applying all fixes, verify:

- [ ] `.env` file exists in project root
- [ ] `SECRET_KEY` is >= 32 characters
- [ ] `JWT_SECRET_KEY` is >= 32 characters
- [ ] `.dockerignore` does NOT block `.env`
- [ ] `docker-compose.fixed.yml` has `env_file:` directive
- [ ] `config_v2_fixed.py` uses lazy loading
- [ ] Containers build without errors
- [ ] `docker exec` shows correct SECRET_KEY
- [ ] Backend logs show "✅ Configuration loaded"
- [ ] Health endpoint returns 200 OK
- [ ] Worker starts without errors

---

## 🛠️ QUICK FIX COMMANDS

```powershell
# 1. Copy fixed files
cp .dockerignore.fixed .dockerignore
cp .env.production .env

# 2. Generate strong secrets
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))" >> .env

# 3. Clean rebuild
docker compose -f deploy/docker-compose.yml down -v
docker compose -f deploy/docker-compose.fixed.yml build --no-cache
docker compose -f deploy/docker-compose.fixed.yml up -d

# 4. Verify
docker logs smart_hiring_backend --tail=50
docker exec -it smart_hiring_backend printenv | grep SECRET
curl http://localhost:8000/api/health
```

---

## 📞 STILL NOT WORKING?

If the error persists after all fixes:

1. **Share exact error logs:**
   ```powershell
   docker logs smart_hiring_backend > backend_logs.txt
   docker exec -it smart_hiring_backend printenv > container_env.txt
   ```

2. **Verify file locations:**
   ```powershell
   Get-ChildItem -Recurse -Include .env,docker-compose*.yml,config.py
   ```

3. **Check Docker version:**
   ```powershell
   docker --version
   docker compose version
   ```

4. **Test config manually:**
   ```powershell
   docker exec -it smart_hiring_backend python
   >>> import os
   >>> os.getenv('SECRET_KEY')
   >>> from config.config_v2_fixed import get_config
   >>> c = get_config()
   >>> print(c.security.SECRET_KEY)
   ```

---

## 🎯 SUCCESS INDICATORS

You'll know it's fixed when you see:

```
✅ Configuration loaded successfully
✅ MongoDB connected
✅ Redis connected
🚀 Starting Smart Hiring System
🌐 Listening on http://0.0.0.0:8000
[INFO] Gunicorn listening at: http://0.0.0.0:8000
```

And:

```powershell
curl http://localhost:8000/api/health
# Returns: {"status": "healthy"}
```

---
