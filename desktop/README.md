# Smart Hiring System - Desktop Application

## Overview

This directory contains the Electron desktop wrapper for the Smart Hiring System. The desktop app provides:

- **Native Windows Application** - Runs as a standalone desktop app
- **Embedded Backend** - Includes the Python backend as a packaged executable
- **System Tray Integration** - Minimize to tray, quick access
- **Auto-Updates** - Automatic update checking and installation
- **Offline Capable** - Works without internet (with local MongoDB)

## Architecture

```
desktop/
├── main.js           # Electron main process (backend management, window creation)
├── preload.js        # Secure bridge between main and renderer
├── renderer.js       # Renderer process logic
├── index.html        # Application UI entry point
├── package.json      # Electron dependencies and build config
├── installer.nsh     # NSIS installer customization
└── assets/          # Icons and images
```

## Features

### Main Process (`main.js`)
- **Backend Process Management**: Spawns and monitors the Python backend executable
- **Window Management**: Creates and manages the main application window
- **System Tray**: Provides system tray icon with context menu
- **Auto Restart**: Automatically restarts backend if it crashes
- **Auto Updates**: Checks for and installs application updates
- **IPC Communication**: Secure communication between processes

### Security
- **Context Isolation**: Enabled to prevent code injection
- **Node Integration**: Disabled in renderer for security
- **Preload Script**: Exposes only necessary APIs via context bridge
- **Content Security Policy**: Strict CSP in HTML

## Development

### Prerequisites
- Node.js 18+ 
- npm 9+
- Python 3.11+ (for backend)
- Visual Studio Build Tools (for native modules)

### Install Dependencies

```powershell
cd desktop
npm install
```

### Run in Development Mode

```powershell
# Start backend separately in another terminal
cd ..\backend
python app.py

# Start Electron app
npm start
# or
npm run dev
```

### Development Tools
- Press `Ctrl+Shift+I` to open DevTools
- Use "Developer > Restart Backend" menu to restart backend
- Backend logs appear in console

## Building

### Build Backend First

Before building the desktop app, you must build the backend executable:

```powershell
cd ..\build_scripts
.\build_backend_exe.ps1
```

This creates `backend/dist/smart_hiring_backend.exe`

### Build Desktop App

```powershell
# Build complete installer
npm run build

# Build unpacked (for testing)
npm run build:dir

# Or use the comprehensive build script
cd ..\build_scripts
.\build_electron_app.ps1
```

### Build Output

The installer will be created at:
```
desktop/dist/Smart Hiring System-Setup-{version}.exe
```

Typical installer size: **150-250 MB** (includes Python runtime, dependencies, Node.js)

## Build Configuration

### electron-builder (`package.json`)

Key settings:
- **appId**: `com.smarthiring.app`
- **Target**: NSIS installer for Windows x64
- **Icon**: `assets/icon.ico` (256x256 minimum)
- **Extra Resources**: Backend executable, config files
- **NSIS Options**: Custom install directory, desktop shortcut, start menu

### NSIS Installer (`installer.nsh`)

Customizations:
- MongoDB installation check and optional install
- Environment file setup from template
- Data retention option on uninstall

## Distribution

### Installer Features

When users run the installer:

1. **Welcome Screen**: Shows app name and version
2. **License Agreement**: Displays MIT license
3. **Install Location**: Choose installation directory (default: `C:\Program Files\Smart Hiring System`)
4. **MongoDB Check**: Detects MongoDB, offers to install if missing
5. **Installation**: Copies files, creates shortcuts
6. **First Run**: Launches app, shows setup wizard

### Installation Paths

- **Application**: `C:\Program Files\Smart Hiring System\`
- **User Data**: `%APPDATA%\smart-hiring-system\`
- **Logs**: `%APPDATA%\smart-hiring-system\logs\`
- **Config**: `%APPDATA%\smart-hiring-system\.env`

### Shortcuts Created

- Desktop: `Smart Hiring System.lnk`
- Start Menu: `Start Menu\Programs\Smart Hiring System\`

## Configuration

The app reads configuration from multiple sources (in priority order):

1. **User Config**: `%APPDATA%\smart-hiring-system\.env`
2. **App Config**: `resources\.env.template` (bundled)
3. **Environment Variables**: System environment variables

### Key Settings

```ini
# Backend Port
PORT=8000

# MongoDB Connection
MONGODB_URI=mongodb://localhost:27017/smart_hiring

# Log Level
LOG_LEVEL=INFO
```

## Auto-Updates

The app checks for updates on startup and periodically:

1. **Check**: Queries GitHub releases for new versions
2. **Download**: Downloads update in background
3. **Notify**: Shows dialog when update is ready
4. **Install**: Restarts app to apply update

### Update Behavior
- **Check Frequency**: On startup + every 24 hours
- **Download**: Automatic (background)
- **Installation**: User prompted
- **Rollback**: Automatic on failure

## Packaging Backend

The backend executable is included via `extraResources`:

```javascript
extraResources: [
  {
    from: "../dist/backend",
    to: "backend",
    filter: ["**/*"]
  }
]
```

At runtime, it's accessed via:
```javascript
path.join(process.resourcesPath, 'backend', 'smart_hiring_backend.exe')
```

## Troubleshooting

### Backend Won't Start

**Symptoms**: "Backend Error" dialog, app hangs on loading

**Solutions**:
1. Check logs: `%APPDATA%\smart-hiring-system\logs\main.log`
2. Verify backend executable exists in install directory
3. Check port 8000 is available: `netstat -ano | findstr :8000`
4. Run backend manually to see errors:
   ```powershell
   cd "C:\Program Files\Smart Hiring System\resources\backend"
   .\smart_hiring_backend.exe
   ```

### Build Fails

**Error**: `electron-builder` fails

**Solutions**:
1. Clear cache: `npm cache clean --force`
2. Delete `node_modules`: `rm -rf node_modules`
3. Reinstall: `npm install`
4. Check backend dist exists: `backend/dist/smart_hiring_backend.exe`
5. Run with verbose logging: `npm run build -- --verbose`

### Missing Dependencies

**Error**: Native module errors

**Solutions**:
1. Install Visual Studio Build Tools
2. Rebuild native modules: `npm rebuild`
3. Use electron-rebuild: `npx electron-rebuild`

### Large Installer Size

**Issue**: Installer > 300 MB

**Optimizations**:
1. Remove unused dependencies
2. Use `package-lock.json` for consistent builds
3. Set `ELECTRON_BUILDER_CACHE` environment variable
4. Use `asar` packaging (enabled by default)

## Testing

### Manual Testing Checklist

- [ ] Backend starts successfully
- [ ] Window opens and loads UI
- [ ] System tray icon appears and works
- [ ] Menu items function correctly
- [ ] Backend restarts on crash
- [ ] App minimizes to tray
- [ ] App restores from tray
- [ ] Window state persists (size, position)
- [ ] External links open in browser
- [ ] Auto-update check works
- [ ] Logs are written correctly
- [ ] Uninstaller removes app properly

### Automated Testing

```powershell
# Run Electron tests (when implemented)
npm test

# Check security
npm audit

# Check for updates
npm outdated
```

## Performance

### Startup Time
- **First Launch**: 3-5 seconds (backend startup)
- **Subsequent**: 2-3 seconds (backend already running)

### Memory Usage
- **Electron**: ~100-150 MB
- **Backend**: ~150-200 MB
- **Total**: ~250-350 MB

### Disk Space
- **Installation**: ~200 MB
- **User Data**: ~50-100 MB (logs, cache)

## Security Considerations

### Implemented
- ✅ Context isolation enabled
- ✅ Node integration disabled in renderer
- ✅ Preload script with minimal API surface
- ✅ Content Security Policy
- ✅ No remote code execution
- ✅ HTTPS for external resources

### Best Practices
- Keep Electron updated
- Regularly update dependencies: `npm audit fix`
- Use code signing for production releases
- Validate all IPC messages
- Sanitize user input

## Code Signing (Production)

For production releases, sign the executable:

### Windows Code Signing

1. Obtain a code signing certificate
2. Set environment variables:
   ```powershell
   $env:CSC_LINK = "path\to\certificate.pfx"
   $env:CSC_KEY_PASSWORD = "certificate_password"
   ```
3. Build with signing:
   ```powershell
   npm run build
   ```

### Benefits of Signing
- No "Unknown Publisher" warnings
- Windows SmartScreen trusts the app
- Professional appearance
- Required for some enterprise deployments

## Future Enhancements

### Planned Features
- [ ] Multiple backend instances support
- [ ] Custom themes
- [ ] Offline mode indicator
- [ ] Background sync when offline
- [ ] Performance monitoring dashboard
- [ ] Plugin system
- [ ] Multi-language support
- [ ] Accessibility improvements

### Technical Debt
- [ ] Add unit tests for main process
- [ ] Add integration tests
- [ ] Implement proper error boundaries
- [ ] Add crash reporting (e.g., Sentry)
- [ ] Optimize bundle size
- [ ] Add telemetry (optional, opt-in)

## Resources

### Documentation
- [Electron Docs](https://www.electronjs.org/docs)
- [electron-builder](https://www.electron.build/)
- [NSIS Documentation](https://nsis.sourceforge.io/Docs/)

### Tools
- [Electron Fiddle](https://www.electronjs.org/fiddle) - Quick prototyping
- [Spectron](https://www.electronjs.org/spectron) - Testing framework
- [Devtron](https://www.electronjs.org/devtron) - DevTools extension

## License

MIT License - See [LICENSE](../LICENSE) file

## Support

- **Documentation**: [docs/USER_GUIDE.md](../docs/USER_GUIDE.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/smart-hiring-system/issues)
- **Email**: support@smarthiring.com
