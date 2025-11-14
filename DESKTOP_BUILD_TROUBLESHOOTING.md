# Desktop App Build Troubleshooting

## Issue Encountered

Building the Electron installer is failing due to **Windows symbolic link permissions** required by the electron-builder code signing tools.

**Error**: `Cannot create symbolic link : A required privilege is not held by the client`

## Solutions

### Option 1: Run in Development Mode (✅ Recommended - No Build Required)

The backend is already deployed and running! You can use the desktop Electron app in **development mode** without building an installer:

```powershell
cd "c:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system\desktop"
npm start
```

This will launch the desktop app that connects to your running backend at http://localhost:5000.

---

### Option 2: Run PowerShell as Administrator

To build the installer successfully, you need to run PowerShell with Administrator rights:

1. **Close current PowerShell**
2. **Right-click PowerShell** → **Run as Administrator**
3. Run the build:

```powershell
cd "c:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system\build_scripts"
.\build_electron_clean.ps1 -SkipBackend
```

---

### Option 3: Enable Developer Mode (Windows 10/11)

This allows creating symbolic links without admin rights:

1. Open **Settings** → **Privacy & Security** → **For developers**
2. Turn ON **Developer Mode**
3. Restart your computer
4. Try building again:

```powershell
cd "c:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system\desktop"
npm run build
```

---

### Option 4: Use the Web Interface (Simplest ✨)

Since your backend is already running, you can just use a **web browser**:

**Open**: http://localhost:5000

This gives you full access to the Smart Hiring System without needing a desktop app!

---

## What's Already Working

✅ **Backend API**: Running on http://localhost:5000  
✅ **Database**: MongoDB initialized and connected  
✅ **Admin Account**: admin@smarthiring.com / changeme  
✅ **All Features**: Job posting, resume upload, AI matching, etc.

---

## Recommended Next Step

**Just run the development desktop app**:

```powershell
cd "c:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system\desktop"
npm start
```

OR

**Use the web interface** at http://localhost:5000

Both options give you full access to the application immediately! 🚀
