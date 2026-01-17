# 🚀 QUICK START - DOCKER SECRET_KEY FIX

## ⚡ 5-MINUTE FIX

### Step 1: Generate Strong Secrets (1 minute)

```powershell
# Generate SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Generate JWT_SECRET_KEY  
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"

# Copy the output - you'll need it in Step 2
```

**Example output:**
```
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
JWT_SECRET_KEY=f2e1d0c9b8a7z6y5x4w3v2u1t0s9r8q7p6o5n4m3l2k1j0i9h8g7f6e5d4c3b2a1
```

---

### Step 2: Update Your `.env` File (1 minute)

```powershell
# Open .env in notepad
notepad .env
```

**Find and replace these lines:**

```ini
# OLD (22 characters - TOO SHORT):
SECRET_KEY=your-flask-secret-key

# NEW (paste your generated 64-character key):
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2

# OLD (placeholder):
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# NEW (paste your generated 64-character key):
JWT_SECRET_KEY=f2e1d0c9b8a7z6y5x4w3v2u1t0s9r8q7p6o5n4m3l2k1j0i9h8g7f6e5d4c3b2a1
```

**Also update these if not already set:**

```ini
MONGO_USERNAME=admin
MONGO_PASSWORD=your_secure_mongo_password_32_chars
REDIS_PASSWORD=your_secure_redis_password_32_chars
ADMIN_PASSWORD=your_secure_admin_password_32_chars
```

**Save and close.**

---

### Step 3: Fix `.dockerignore` (30 seconds)

```powershell
# Use the fixed version
cp .dockerignore.fixed .dockerignore
```

**OR manually edit `.dockerignore`:**

```powershell
notepad .dockerignore
```

Find these lines:
```
.env
.env.local
.env.production
```

**Comment them out by adding `#`:**
```
# .env
# .env.local
# .env.production
```

**Save and close.**

---

### Step 4: Clean & Rebuild (2 minutes)

```powershell
# Stop and remove everything
docker compose -f deploy/docker-compose.yml down -v

# Clean Docker cache
docker system prune -af

# Build with fixed compose file
docker compose -f deploy/docker-compose.fixed.yml build --no-cache

# Start services
docker compose -f deploy/docker-compose.fixed.yml up -d
```

---

### Step 5: Verify (30 seconds)

```powershell
# Check container status (all should be "Up")
docker compose -f deploy/docker-compose.fixed.yml ps

# Check backend logs (should show "Configuration loaded")
docker logs smart_hiring_backend --tail=20

# Test health endpoint (should return {"status": "healthy"})
curl http://localhost:8000/api/health
```

---

## ✅ SUCCESS INDICATORS

You'll see:
```
✅ Configuration loaded successfully
🚀 Starting Smart Hiring System
🌐 Listening on http://0.0.0.0:8000
```

**Test API:**
```powershell
curl http://localhost:8000/api/health
```

**Expected response:**
```json
{"status": "healthy", "timestamp": "2025-12-07T..."}
```

---

## ❌ IF IT STILL FAILS

### Check environment variables inside container:

```powershell
docker exec -it smart_hiring_backend printenv | Select-String "SECRET"
```

**Should show:**
```
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6...
JWT_SECRET_KEY=f2e1d0c9b8a7z6y5x4w3v2u1t0s9r8q7...
```

**If SECRET_KEY is missing or wrong:**
```powershell
# Re-check .env file
Get-Content .env | Select-String "SECRET_KEY"

# Re-check .dockerignore
Get-Content .dockerignore | Select-String "^\.env"

# If .env is blocked, fix it:
cp .dockerignore.fixed .dockerignore

# Rebuild:
docker compose -f deploy/docker-compose.fixed.yml build --no-cache
docker compose -f deploy/docker-compose.fixed.yml up -d --force-recreate
```

---

## 📋 AUTOMATED SCRIPT

**Run the complete automated fix:**

```powershell
# Execute automated rebuild script
.\DOCKER_REBUILD.ps1
```

This script will:
1. ✅ Verify .env exists and is valid
2. ✅ Check .dockerignore configuration
3. ✅ Clean Docker environment
4. ✅ Build with no cache
5. ✅ Start all services
6. ✅ Run health checks
7. ✅ Show debugging commands

---

## 🎯 QUICK REFERENCE

**Files you need:**
- ✅ `.env` (with strong 64-char secrets)
- ✅ `.dockerignore.fixed` (or modified .dockerignore)
- ✅ `docker-compose.fixed.yml`

**Commands you need:**
```powershell
# Generate secrets
python -c "import secrets; print(secrets.token_hex(32))"

# Clean rebuild
docker compose down -v
docker system prune -af
docker compose -f deploy/docker-compose.fixed.yml build --no-cache
docker compose -f deploy/docker-compose.fixed.yml up -d

# Verify
docker logs smart_hiring_backend --tail=20
curl http://localhost:8000/api/health
```

---

## 🆘 STILL STUCK?

**Read the detailed guides:**
- 📖 `COMPLETE_FIX_SUMMARY.md` - Full analysis
- 🔧 `TROUBLESHOOTING_GUIDE.md` - Step-by-step debugging
- 📋 `DOCKER_REBUILD.ps1` - Automated rebuild script

**Or contact support with:**
```powershell
docker logs smart_hiring_backend > logs.txt
docker exec -it smart_hiring_backend printenv > env.txt
```

---

**Your Docker environment will be fixed in 5 minutes. Let's go! 🚀**
