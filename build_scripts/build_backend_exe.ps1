# PowerShell Script to Build Backend Executable using PyInstaller
# Run this from the project root directory

param(
    [string]$OutputDir = "dist",
    [switch]$Clean = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Smart Hiring System - Backend Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set error action preference
$ErrorActionPreference = "Stop"

# Get project root
$ProjectRoot = $PSScriptRoot | Split-Path -Parent
$BackendDir = Join-Path $ProjectRoot "backend"
$VenvDir = Join-Path $ProjectRoot ".venv"
$DistDir = Join-Path $ProjectRoot $OutputDir
$BuildDir = Join-Path $ProjectRoot "build"

Write-Host "📁 Project Root: $ProjectRoot" -ForegroundColor Yellow
Write-Host "📁 Backend Dir: $BackendDir" -ForegroundColor Yellow
Write-Host "📁 Output Dir: $DistDir" -ForegroundColor Yellow
Write-Host ""

# Clean previous builds if requested
if ($Clean) {
    Write-Host "🧹 Cleaning previous builds..." -ForegroundColor Yellow
    if (Test-Path $DistDir) {
        Remove-Item $DistDir -Recurse -Force
        Write-Host "   ✓ Removed dist directory" -ForegroundColor Green
    }
    if (Test-Path $BuildDir) {
        Remove-Item $BuildDir -Recurse -Force
        Write-Host "   ✓ Removed build directory" -ForegroundColor Green
    }
    Write-Host ""
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path $VenvDir)) {
    Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $VenvDir
    Write-Host "   ✓ Virtual environment created" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
& $ActivateScript
Write-Host "   ✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "   ✓ Pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
$RequirementsFile = Join-Path $BackendDir "requirements.txt"
if (Test-Path $RequirementsFile) {
    pip install -r $RequirementsFile --quiet
    Write-Host "   ✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  requirements.txt not found, installing core packages..." -ForegroundColor Yellow
    pip install Flask pymongo flask-cors flask-jwt-extended flask-bcrypt python-dotenv --quiet
}
Write-Host ""

# Install PyInstaller
Write-Host "📦 Installing PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller --quiet
Write-Host "   ✓ PyInstaller installed" -ForegroundColor Green
Write-Host ""

# Verify main.py exists
$MainPy = Join-Path $BackendDir "main.py"
if (-not (Test-Path $MainPy)) {
    Write-Host "❌ Error: main.py not found in backend directory" -ForegroundColor Red
    exit 1
}

# Build executable with PyInstaller
Write-Host "🔨 Building executable with PyInstaller..." -ForegroundColor Cyan
Write-Host "   This may take several minutes..." -ForegroundColor Yellow
Write-Host ""

Set-Location $BackendDir

$PyInstallerArgs = @(
    "--onefile",
    "--name", "smart_hiring_backend",
    "--add-data", "ml_models;ml_models",
    "--add-data", "smart_hiring_resumes;smart_hiring_resumes",
    "--add-data", "services;services",
    "--add-data", "utils;utils",
    "--add-data", "models;models",
    "--add-data", "routes;routes",
    "--hidden-import", "flask",
    "--hidden-import", "pymongo",
    "--hidden-import", "sklearn",
    "--hidden-import", "spacy",
    "--hidden-import", "bcrypt",
    "--hidden-import", "jwt",
    "--hidden-import", "dotenv",
    "--collect-all", "flask",
    "--collect-all", "flask_cors",
    "--collect-all", "flask_jwt_extended",
    "--noconfirm",
    "main.py"
)

try {
    pyinstaller @PyInstallerArgs
    Write-Host ""
    Write-Host "   ✓ Executable built successfully" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "❌ Error building executable: $_" -ForegroundColor Red
    Set-Location $ProjectRoot
    exit 1
}

Set-Location $ProjectRoot

# Copy additional files to dist
Write-Host ""
Write-Host "📋 Copying additional files..." -ForegroundColor Yellow

$BackendDistDir = Join-Path $DistDir "backend"
if (-not (Test-Path $BackendDistDir)) {
    New-Item -ItemType Directory -Path $BackendDistDir -Force | Out-Null
}

# Copy exe from backend/dist to main dist
$ExeSource = Join-Path $BackendDir "dist\smart_hiring_backend.exe"
$ExeDest = Join-Path $BackendDistDir "smart_hiring_backend.exe"
if (Test-Path $ExeSource) {
    Copy-Item $ExeSource $ExeDest -Force
    Write-Host "   ✓ Copied executable to $BackendDistDir" -ForegroundColor Green
}

# Copy .env.template
$EnvTemplate = Join-Path $ProjectRoot ".env.template"
if (Test-Path $EnvTemplate) {
    Copy-Item $EnvTemplate $BackendDistDir -Force
    Write-Host "   ✓ Copied .env.template" -ForegroundColor Green
}

# Copy config directory
$ConfigDir = Join-Path $ProjectRoot "config"
if (Test-Path $ConfigDir) {
    Copy-Item $ConfigDir $BackendDistDir -Recurse -Force
    Write-Host "   ✓ Copied config directory" -ForegroundColor Green
}

# Create logs directory
$LogsDir = Join-Path $BackendDistDir "logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
    Write-Host "   ✓ Created logs directory" -ForegroundColor Green
}

Write-Host ""

# Test the executable
Write-Host "🧪 Testing executable..." -ForegroundColor Cyan
$ExePath = Join-Path $BackendDistDir "smart_hiring_backend.exe"

if (Test-Path $ExePath) {
    Write-Host "   ✓ Executable found: $ExePath" -ForegroundColor Green
    
    # Get file size
    $FileSize = (Get-Item $ExePath).Length / 1MB
    Write-Host "   📊 File size: $([math]::Round($FileSize, 2)) MB" -ForegroundColor Yellow
    
    Write-Host ""
    Write-Host "   To test the executable, run:" -ForegroundColor Yellow
    Write-Host "   $ExePath" -ForegroundColor Cyan
} else {
    Write-Host "   ❌ Executable not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ Build completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📦 Output location: $BackendDistDir" -ForegroundColor Cyan
Write-Host "🚀 Run the executable: $ExePath" -ForegroundColor Cyan
Write-Host ""
