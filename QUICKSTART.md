# Quick Start - Building the Desktop Application

## Prerequisites

Before building the Smart Hiring System desktop application, ensure you have:

✅ **Node.js 18+** - [Download](https://nodejs.org/)  
✅ **Python 3.11+** - [Download](https://www.python.org/)  
✅ **Git** - [Download](https://git-scm.com/)  
✅ **Visual Studio Build Tools** (Windows) - For native modules

## Quick Build (5 Minutes)

### Step 1: Install Desktop Dependencies

```powershell
cd desktop
npm install
```

This installs Electron, electron-builder, and required dependencies (~200 MB).

### Step 2: Build Backend Executable

```powershell
cd ..\build_scripts
.\build_backend_exe.ps1
```

This creates `backend/dist/smart_hiring_backend.exe` (~150 MB).

**Expected output**: ✓ Backend build completed successfully

### Step 3: Build Desktop Installer

```powershell
.\build_electron_app.ps1
```

This creates the complete Windows installer (~200 MB).

**Output location**: `desktop/dist/Smart Hiring System-Setup-1.0.0.exe`

### Step 4: Test the Installer

```powershell
# Run the installer
cd ..\desktop\dist
.\Smart*.exe
```

## Development Mode

To run the app in development without building:

### Terminal 1: Start Backend
```powershell
cd backend
python app.py
```

### Terminal 2: Start Electron
```powershell
cd desktop
npm run dev
```

The app will connect to the backend at `http://localhost:8000`.

## Build Options

### Full Build (Recommended)
```powershell
.\build_electron_app.ps1
```
Creates complete installer with all dependencies.

### Quick Build (Testing)
```powershell
.\build_electron_app.ps1 -Dev
```
Creates unpacked directory for faster testing.

### Clean Build (Fresh Start)
```powershell
.\build_electron_app.ps1 -Clean
```
Removes all previous builds and rebuilds from scratch.

### Skip Steps
```powershell
# Skip backend (if already built)
.\build_electron_app.ps1 -SkipBackend

# Skip frontend (if not ready)
.\build_electron_app.ps1 -SkipFrontend
```

## Troubleshooting

### "node is not recognized"
**Solution**: Install Node.js and restart PowerShell  
[Download Node.js](https://nodejs.org/)

### "python is not recognized"  
**Solution**: Install Python and add to PATH  
[Download Python](https://www.python.org/)

### "npm install" fails with gyp errors
**Solution**: Install Visual Studio Build Tools  
```powershell
npm install --global windows-build-tools
```

### Backend build fails
**Solution**: Check Python virtual environment  
```powershell
cd ..
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### Electron build fails
**Solution**: Clear cache and reinstall  
```powershell
cd desktop
Remove-Item -Recurse -Force node_modules
npm cache clean --force
npm install
```

### Port 8000 already in use
**Solution**: Kill existing process  
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

## What Gets Built

### Backend Executable
- **File**: `backend/dist/smart_hiring_backend.exe`
- **Size**: ~150 MB
- **Contents**: Python 3.11 runtime, Flask, dependencies, ML models
- **Standalone**: Runs without Python installation

### Desktop Installer
- **File**: `desktop/dist/Smart Hiring System-Setup-1.0.0.exe`
- **Size**: ~200-250 MB
- **Type**: NSIS installer for Windows
- **Architecture**: x64 only

### Installed Application
- **Location**: `C:\Program Files\Smart Hiring System\`
- **Data**: `%APPDATA%\smart-hiring-system\`
- **Size**: ~300 MB total

## Build Time Estimates

| Step | Time | Output Size |
|------|------|-------------|
| npm install | 2-3 min | 200 MB |
| Backend build | 3-5 min | 150 MB |
| Electron build | 5-7 min | 250 MB |
| **Total** | **10-15 min** | **600 MB** |

*Times vary based on system performance and internet speed.*

## Next Steps

After building:

1. **Test the Installer**
   ```powershell
   .\desktop\dist\Smart*.exe
   ```

2. **Run the Application**
   - Look for desktop shortcut: "Smart Hiring System"
   - Or: Start Menu → Smart Hiring System

3. **First-Time Setup**
   - Configure MongoDB connection
   - Create admin account
   - Set up SMTP (optional)

4. **Verify Features**
   - Upload test resume
   - Create test job posting
   - Run matching algorithm
   - Check dashboard analytics

## Distribution

### For Testing
- Share the `.exe` installer file directly
- Size: ~250 MB
- Users just double-click to install

### For Production
1. **Code Sign** the executable (removes security warnings)
2. **Host** on GitHub Releases or your website
3. **Document** system requirements
4. **Provide** quick start guide

### System Requirements (End Users)

**Minimum**:
- Windows 10 (64-bit)
- 4 GB RAM
- 1 GB disk space
- Internet connection (for MongoDB Atlas)

**Recommended**:
- Windows 11 (64-bit)
- 8 GB RAM
- 2 GB disk space
- Local MongoDB installation

## Getting Help

### Documentation
- **Desktop App**: `desktop/README.md`
- **User Guide**: `docs/USER_GUIDE.md`
- **Build Guide**: This file

### Support
- Check logs: `%APPDATA%\smart-hiring-system\logs\`
- GitHub Issues: Report problems
- Email: support@smarthiring.com

## Success Checklist

After completing the quick start, you should have:

- [x] Node.js and Python installed
- [x] Desktop dependencies installed (`desktop/node_modules/`)
- [x] Backend executable built (`backend/dist/smart_hiring_backend.exe`)
- [x] Desktop installer created (`desktop/dist/Smart Hiring System-Setup-1.0.0.exe`)
- [x] Installer tested and working
- [x] Application launches successfully
- [x] Backend connects and health check passes

**Congratulations!** 🎉 You've successfully built the Smart Hiring System desktop application!
