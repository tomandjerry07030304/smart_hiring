# Complete Startup Script for Smart Hiring System

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Smart Hiring System - Complete Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Start MongoDB
Write-Host "[1/4] Starting MongoDB Server..." -ForegroundColor Yellow
Start-Job -ScriptBlock {
    & "C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe" --dbpath "C:\data\db"
} | Out-Null

Start-Sleep -Seconds 3
Write-Host "MongoDB is starting in background..." -ForegroundColor Green
Write-Host ""

# Step 2: Activate Virtual Environment
Write-Host "[2/4] Activating Python Environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Step 3: Initialize Database (first time only)
Write-Host "[3/4] Would you like to initialize the database? (y/n)" -ForegroundColor Yellow
$init = Read-Host "Enter choice"
if ($init -eq "y") {
    Write-Host "Initializing database..." -ForegroundColor Yellow
    python backend/scripts/init_db.py
    python backend/scripts/seed_db.py
    Write-Host "Database initialized with sample data!" -ForegroundColor Green
}
Write-Host ""

# Step 4: Start Application
Write-Host "[4/4] Starting Smart Hiring System API..." -ForegroundColor Yellow
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""
python backend/app.py
