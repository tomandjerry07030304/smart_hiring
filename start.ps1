# Smart Hiring System - Quick Start Script
# Run this script to start the application

Write-Host "🚀 Smart Hiring System - Quick Start" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "📍 Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "   $pythonVersion" -ForegroundColor Green

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "⚠️  Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "   ✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check if dependencies are installed
Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow
$installed = pip list --format=freeze
if ($installed -notmatch "flask") {
    Write-Host "   📥 Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    Write-Host "   ✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ✅ Dependencies already installed" -ForegroundColor Green
}

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "   ✅ .env file created. Please edit with your settings." -ForegroundColor Green
    Write-Host "   ⚠️  Don't forget to configure MongoDB URI in .env!" -ForegroundColor Red
    Write-Host ""
}

# Ask user what to do
Write-Host "What would you like to do?" -ForegroundColor Cyan
Write-Host "1. Initialize database (first time setup)" -ForegroundColor White
Write-Host "2. Seed database with sample data" -ForegroundColor White
Write-Host "3. Start the application" -ForegroundColor White
Write-Host "4. Run all (init + seed + start)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "🔄 Initializing database..." -ForegroundColor Yellow
        python backend/scripts/init_db.py
    }
    "2" {
        Write-Host "🌱 Seeding database..." -ForegroundColor Yellow
        python backend/scripts/seed_db.py
    }
    "3" {
        Write-Host "🚀 Starting application..." -ForegroundColor Yellow
        Write-Host ""
        python backend/app.py
    }
    "4" {
        Write-Host "🔄 Initializing database..." -ForegroundColor Yellow
        python backend/scripts/init_db.py
        Write-Host ""
        Write-Host "🌱 Seeding database..." -ForegroundColor Yellow
        python backend/scripts/seed_db.py
        Write-Host ""
        Write-Host "🚀 Starting application..." -ForegroundColor Yellow
        Write-Host ""
        python backend/app.py
    }
    default {
        Write-Host "❌ Invalid choice. Exiting." -ForegroundColor Red
    }
}
