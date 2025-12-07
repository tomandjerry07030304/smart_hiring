# ============================================================================
# DOCKER ENVIRONMENT REBUILD & DEBUGGING SCRIPT
# ============================================================================
# Execute these commands in PowerShell (Windows) or Bash (Linux/Mac)
# This script performs a complete clean rebuild of your Docker environment
# ============================================================================

# ============================================================================
# STEP 1: STOP ALL RUNNING CONTAINERS
# ============================================================================
Write-Host "🛑 STEP 1: Stopping all containers..." -ForegroundColor Cyan

docker compose -f deploy/docker-compose.yml down

# Alternative if you're using old docker-compose command:
# docker-compose -f deploy/docker-compose.yml down

# ============================================================================
# STEP 2: REMOVE ALL VOLUMES (DESTRUCTIVE - DELETES DATA!)
# ============================================================================
Write-Host "🗑️  STEP 2: Removing all volumes (this deletes database data)..." -ForegroundColor Yellow
Write-Host "⚠️  WARNING: This will delete MongoDB data, Redis data, logs, uploads!" -ForegroundColor Red
Write-Host "Press Ctrl+C within 5 seconds to cancel..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

docker compose -f deploy/docker-compose.yml down -v

# ============================================================================
# STEP 3: DEEP CLEAN DOCKER SYSTEM
# ============================================================================
Write-Host "🧹 STEP 3: Deep cleaning Docker system..." -ForegroundColor Cyan

# Remove all stopped containers
docker container prune -f

# Remove all unused images
docker image prune -af

# Remove all unused volumes
docker volume prune -f

# Remove all unused networks
docker network prune -f

# Nuclear option (removes EVERYTHING - use with extreme caution):
# docker system prune -af --volumes

# ============================================================================
# STEP 4: VERIFY .ENV FILE EXISTS AND IS CORRECT
# ============================================================================
Write-Host "🔍 STEP 4: Verifying .env file..." -ForegroundColor Cyan

if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
    
    # Check SECRET_KEY length
    $envContent = Get-Content .env -Raw
    if ($envContent -match 'SECRET_KEY=(.+)') {
        $secretKey = $matches[1].Trim()
        $keyLength = $secretKey.Length
        
        Write-Host "SECRET_KEY length: $keyLength characters" -ForegroundColor Yellow
        
        if ($keyLength -lt 32) {
            Write-Host "❌ ERROR: SECRET_KEY is too short ($keyLength chars)" -ForegroundColor Red
            Write-Host "Minimum required: 32 characters" -ForegroundColor Red
            Write-Host "Generate a new key with:" -ForegroundColor Yellow
            Write-Host '  python -c "import secrets; print(secrets.token_hex(32))"' -ForegroundColor Cyan
            exit 1
        } else {
            Write-Host "✅ SECRET_KEY length is adequate" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠️  WARNING: SECRET_KEY not found in .env file" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Copy .env.production to .env and fill in the values:" -ForegroundColor Yellow
    Write-Host "  cp .env.production .env" -ForegroundColor Cyan
    exit 1
}

# ============================================================================
# STEP 5: VERIFY .DOCKERIGNORE IS CORRECT
# ============================================================================
Write-Host "🔍 STEP 5: Checking .dockerignore..." -ForegroundColor Cyan

if (Test-Path ".dockerignore") {
    $dockerignoreContent = Get-Content .dockerignore -Raw
    
    # Check if .env is blocked
    if ($dockerignoreContent -match '^\s*\.env\s*$' -or $dockerignoreContent -match '\n\.env\n') {
        Write-Host "⚠️  WARNING: .env is blocked in .dockerignore!" -ForegroundColor Yellow
        Write-Host "This prevents environment variables from being available in Docker." -ForegroundColor Yellow
        Write-Host "Solution: Use .dockerignore.fixed or comment out .env line" -ForegroundColor Cyan
    } else {
        Write-Host "✅ .dockerignore looks correct" -ForegroundColor Green
    }
}

# ============================================================================
# STEP 6: BUILD IMAGES WITH NO CACHE
# ============================================================================
Write-Host "🔨 STEP 6: Building Docker images (this may take several minutes)..." -ForegroundColor Cyan

docker compose -f deploy/docker-compose.fixed.yml build --no-cache --progress=plain

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Docker build failed!" -ForegroundColor Red
    Write-Host "Check the error messages above for details." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Build completed successfully" -ForegroundColor Green

# ============================================================================
# STEP 7: START CONTAINERS
# ============================================================================
Write-Host "🚀 STEP 7: Starting containers..." -ForegroundColor Cyan

docker compose -f deploy/docker-compose.fixed.yml up -d --force-recreate

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Failed to start containers!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Containers started" -ForegroundColor Green

# ============================================================================
# STEP 8: WAIT FOR SERVICES TO BE HEALTHY
# ============================================================================
Write-Host "⏳ STEP 8: Waiting for services to become healthy..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Check container status
docker compose -f deploy/docker-compose.fixed.yml ps

# ============================================================================
# STEP 9: CHECK LOGS FOR ERRORS
# ============================================================================
Write-Host "📋 STEP 9: Checking backend logs for errors..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

docker logs smart_hiring_backend --tail=50

Write-Host ""
Write-Host "If you see 'ValueError: SECRET_KEY must be set' above, run:" -ForegroundColor Yellow
Write-Host "  docker exec -it smart_hiring_backend printenv | grep SECRET" -ForegroundColor Cyan

# ============================================================================
# DEBUGGING COMMANDS
# ============================================================================
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Magenta
Write-Host "DEBUGGING COMMANDS" -ForegroundColor Magenta
Write-Host "============================================================================" -ForegroundColor Magenta
Write-Host ""

Write-Host "1️⃣  View backend logs:" -ForegroundColor Cyan
Write-Host "   docker logs smart_hiring_backend -f" -ForegroundColor White
Write-Host ""

Write-Host "2️⃣  View worker logs:" -ForegroundColor Cyan
Write-Host "   docker logs smart_hiring_worker -f" -ForegroundColor White
Write-Host ""

Write-Host "3️⃣  Check environment variables inside backend:" -ForegroundColor Cyan
Write-Host '   docker exec -it smart_hiring_backend printenv | grep -E "(SECRET|JWT|MONGO)"' -ForegroundColor White
Write-Host ""

Write-Host "4️⃣  Check environment variables inside worker:" -ForegroundColor Cyan
Write-Host '   docker exec -it smart_hiring_worker printenv | grep -E "(SECRET|JWT|MONGO)"' -ForegroundColor White
Write-Host ""

Write-Host "5️⃣  Enter backend container shell:" -ForegroundColor Cyan
Write-Host "   docker exec -it smart_hiring_backend /bin/bash" -ForegroundColor White
Write-Host ""

Write-Host "6️⃣  Test config loading inside container:" -ForegroundColor Cyan
Write-Host '   docker exec -it smart_hiring_backend python -c "from config.config_v2_fixed import get_config; c = get_config(); print(c.get_summary())"' -ForegroundColor White
Write-Host ""

Write-Host "7️⃣  Check if .env file exists in container:" -ForegroundColor Cyan
Write-Host "   docker exec -it smart_hiring_backend ls -la /app/.env" -ForegroundColor White
Write-Host ""

Write-Host "8️⃣  View container resource usage:" -ForegroundColor Cyan
Write-Host "   docker stats" -ForegroundColor White
Write-Host ""

Write-Host "9️⃣  Restart specific service:" -ForegroundColor Cyan
Write-Host "   docker compose -f deploy/docker-compose.fixed.yml restart backend" -ForegroundColor White
Write-Host ""

Write-Host "🔟 Stop all services:" -ForegroundColor Cyan
Write-Host "   docker compose -f deploy/docker-compose.fixed.yml down" -ForegroundColor White
Write-Host ""

Write-Host "============================================================================" -ForegroundColor Magenta
Write-Host "✅ REBUILD COMPLETE!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "Your application should now be running at:" -ForegroundColor Yellow
Write-Host "  🌐 Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test the backend health endpoint:" -ForegroundColor Yellow
Write-Host "  curl http://localhost:8000/api/health" -ForegroundColor Cyan
Write-Host ""
