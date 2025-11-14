# Build Electron Desktop Application
# Builds complete Windows installer with backend and frontend

param(
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$Clean,
    [switch]$Dev
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Configuration
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
$DESKTOP_DIR = Join-Path $PROJECT_ROOT "desktop"
$BACKEND_DIR = Join-Path $PROJECT_ROOT "backend"
$FRONTEND_DIR = Join-Path $PROJECT_ROOT "frontend"
$BUILD_DIR = Join-Path $PROJECT_ROOT "dist"
$VENV_PATH = Join-Path $PROJECT_ROOT ".venv"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Smart Hiring System - Electron Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function: Check if command exists
function Test-Command {
    param([string]$Command)
    return [bool](Get-Command -Name $Command -ErrorAction SilentlyContinue)
}

# Function: Install Node dependencies
function Install-NodeDependencies {
    param([string]$Directory)
    
    Write-Host "Installing Node dependencies in $Directory..." -ForegroundColor Yellow
    Push-Location $Directory
    try {
        if (Test-Path "package-lock.json") {
            npm ci
        } else {
            npm install
        }
        Write-Host "✓ Node dependencies installed" -ForegroundColor Green
    }
    finally {
        Pop-Location
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

if (-not (Test-Command "node")) {
    Write-Host "✗ Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

$nodeVersion = node --version
Write-Host "✓ Node.js version: $nodeVersion" -ForegroundColor Green

if (-not (Test-Command "npm")) {
    Write-Host "✗ npm is not installed" -ForegroundColor Red
    exit 1
}

Write-Host "✓ npm version: $(npm --version)" -ForegroundColor Green

if (-not (Test-Command "python")) {
    Write-Host "✗ Python is not installed. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Python version: $(python --version)" -ForegroundColor Green
Write-Host ""

# Clean previous builds
if ($Clean) {
    Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
    
    $dirsToClean = @(
        (Join-Path $DESKTOP_DIR "dist"),
        (Join-Path $DESKTOP_DIR "node_modules"),
        (Join-Path $BACKEND_DIR "dist"),
        (Join-Path $BACKEND_DIR "build"),
        (Join-Path $FRONTEND_DIR "build"),
        (Join-Path $FRONTEND_DIR "node_modules"),
        $BUILD_DIR
    )
    
    foreach ($dir in $dirsToClean) {
        if (Test-Path $dir) {
            Write-Host "  Removing $dir..."
            Remove-Item -Path $dir -Recurse -Force
        }
    }
    
    Write-Host "✓ Clean completed" -ForegroundColor Green
    Write-Host ""
}

# Step 1: Build Backend
if (-not $SkipBackend) {
    Write-Host "Step 1: Building Backend..." -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    
    $backendBuildScript = Join-Path $PROJECT_ROOT "build_scripts" "build_backend_exe.ps1"
    
    if (Test-Path $backendBuildScript) {
        & $backendBuildScript
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Backend build failed" -ForegroundColor Red
            exit 1
        }
        
        # Verify backend dist exists
        $backendDist = Join-Path $BACKEND_DIR "dist"
        if (-not (Test-Path $backendDist)) {
            Write-Host "✗ Backend dist directory not found at $backendDist" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "✓ Backend build completed" -ForegroundColor Green
    } else {
        Write-Host "⚠ Backend build script not found, skipping backend build" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

# Step 2: Build Frontend (if exists)
if (-not $SkipFrontend) {
    Write-Host "Step 2: Building Frontend..." -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    
    if (Test-Path (Join-Path $FRONTEND_DIR "package.json")) {
        Install-NodeDependencies -Directory $FRONTEND_DIR
        
        Push-Location $FRONTEND_DIR
        try {
            Write-Host "Building React application..." -ForegroundColor Yellow
            npm run build
            
            $frontendBuild = Join-Path $FRONTEND_DIR "build"
            if (Test-Path $frontendBuild) {
                Write-Host "✓ Frontend build completed" -ForegroundColor Green
            } else {
                Write-Host "✗ Frontend build directory not found" -ForegroundColor Red
                exit 1
            }
        }
        finally {
            Pop-Location
        }
    } else {
        Write-Host "⚠ Frontend package.json not found, skipping frontend build" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

# Step 3: Setup Desktop App
Write-Host "Step 3: Setting up Electron App..." -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

Install-NodeDependencies -Directory $DESKTOP_DIR

# Copy backend dist to desktop resources
Write-Host "Copying backend to desktop resources..." -ForegroundColor Yellow
$backendSource = Join-Path $BACKEND_DIR "dist"
$backendTarget = Join-Path $BUILD_DIR "backend"

if (Test-Path $backendSource) {
    if (Test-Path $backendTarget) {
        Remove-Item -Path $backendTarget -Recurse -Force
    }
    Copy-Item -Path $backendSource -Destination $backendTarget -Recurse
    Write-Host "✓ Backend copied to build directory" -ForegroundColor Green
} else {
    Write-Host "⚠ Backend dist not found, installer may not work correctly" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Build Electron Application
Write-Host "Step 4: Building Electron Application..." -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Push-Location $DESKTOP_DIR
try {
    if ($Dev) {
        Write-Host "Building development package (unpacked)..." -ForegroundColor Yellow
        npm run build:dir
    } else {
        Write-Host "Building production installer..." -ForegroundColor Yellow
        npm run build
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Electron build failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✓ Electron build completed" -ForegroundColor Green
}
finally {
    Pop-Location
}

Write-Host ""

# Step 5: Verify output
Write-Host "Step 5: Verifying Build..." -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

$installerPath = Join-Path $DESKTOP_DIR "dist" "Smart Hiring System-Setup-*.exe"
$installers = Get-ChildItem -Path (Join-Path $DESKTOP_DIR "dist") -Filter "Smart Hiring System-Setup-*.exe" -ErrorAction SilentlyContinue

if ($installers.Count -gt 0) {
    Write-Host "✓ Installer(s) created successfully:" -ForegroundColor Green
    
    foreach ($installer in $installers) {
        $sizeGB = [math]::Round($installer.Length / 1GB, 2)
        $sizeMB = [math]::Round($installer.Length / 1MB, 2)
        
        Write-Host ""
        Write-Host "  File: $($installer.Name)" -ForegroundColor White
        Write-Host "  Path: $($installer.FullName)" -ForegroundColor Gray
        Write-Host "  Size: $sizeMB MB ($sizeGB GB)" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "BUILD COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Test the installer by running it on a clean Windows machine" -ForegroundColor White
    Write-Host "2. Verify all features work correctly" -ForegroundColor White
    Write-Host "3. Check the logs at: %APPDATA%\smart-hiring-system\logs" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "✗ Installer not found in expected location" -ForegroundColor Red
    Write-Host "  Expected: $installerPath" -ForegroundColor Gray
    
    # List what's in the dist directory
    $distDir = Join-Path $DESKTOP_DIR "dist"
    if (Test-Path $distDir) {
        Write-Host ""
        Write-Host "Contents of dist directory:" -ForegroundColor Yellow
        Get-ChildItem -Path $distDir | ForEach-Object {
            Write-Host "  $($_.Name)" -ForegroundColor Gray
        }
    }
    
    exit 1
}

# Optional: Copy to project root dist
$rootDist = Join-Path $PROJECT_ROOT "dist"
if (-not (Test-Path $rootDist)) {
    New-Item -ItemType Directory -Path $rootDist | Out-Null
}

Write-Host "Copying installer to project root dist..." -ForegroundColor Yellow
foreach ($installer in $installers) {
    Copy-Item -Path $installer.FullName -Destination $rootDist -Force
    Write-Host "✓ Copied to: $(Join-Path $rootDist $installer.Name)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Build artifacts location:" -ForegroundColor Cyan
Write-Host "  Desktop dist: $(Join-Path $DESKTOP_DIR 'dist')" -ForegroundColor White
Write-Host "  Project dist: $rootDist" -ForegroundColor White
Write-Host ""
