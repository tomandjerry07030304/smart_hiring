/**
 * Smart Hiring System - Electron Main Process
 * Manages application lifecycle, backend process, and window creation
 */

const { app, BrowserWindow, ipcMain, Menu, Tray, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const log = require('electron-log');
const Store = require('electron-store');
const { autoUpdater } = require('electron-updater');

// Configure logging
log.transports.file.level = 'info';
log.transports.console.level = 'debug';

// Initialize persistent storage
const store = new Store();

// Global references
let mainWindow = null;
let backendProcess = null;
let tray = null;
let isQuitting = false;

// Configuration
const CONFIG = {
  backendPort: process.env.PORT || 8000,
  backendHost: 'localhost',
  isDev: process.argv.includes('--dev') || !app.isPackaged,
  backendPath: null,
  maxRestartAttempts: 3,
  restartDelay: 2000
};

// Determine backend executable path
if (CONFIG.isDev) {
  CONFIG.backendPath = path.join(__dirname, '..', 'backend', 'main.py');
} else {
  CONFIG.backendPath = path.join(process.resourcesPath, 'backend', 'smart_hiring_backend.exe');
}

log.info('Application starting...', {
  isDev: CONFIG.isDev,
  backendPath: CONFIG.backendPath,
  version: app.getVersion()
});

/**
 * Create the main application window
 */
function createWindow() {
  const windowState = store.get('windowState', {
    width: 1280,
    height: 800,
    maximized: false
  });

  mainWindow = new BrowserWindow({
    width: windowState.width,
    height: windowState.height,
    minWidth: 1024,
    minHeight: 768,
    icon: path.join(__dirname, 'assets', 'icon.ico'),
    title: 'Smart Hiring System',
    backgroundColor: '#ffffff',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: true
    },
    show: false
  });

  // Load the application
  const startUrl = CONFIG.isDev 
    ? 'http://localhost:3000'
    : `http://${CONFIG.backendHost}:${CONFIG.backendPort}`;

  mainWindow.loadURL(startUrl).catch(err => {
    log.error('Failed to load URL:', err);
    showErrorDialog('Failed to start application', 
      'Could not connect to the backend server. Please try restarting the application.');
  });

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    if (windowState.maximized) {
      mainWindow.maximize();
    }
    mainWindow.show();
    mainWindow.focus();
  });

  // Save window state on close
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      return false;
    }

    const bounds = mainWindow.getBounds();
    store.set('windowState', {
      width: bounds.width,
      height: bounds.height,
      maximized: mainWindow.isMaximized()
    });
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Development tools
  if (CONFIG.isDev) {
    mainWindow.webContents.openDevTools();
  }

  createMenu();
  createTray();
}

/**
 * Start the backend process
 */
function startBackend() {
  if (backendProcess) {
    log.warn('Backend process already running');
    return;
  }

  log.info('Starting backend process...');

  try {
    const options = {
      env: {
        ...process.env,
        PORT: CONFIG.backendPort.toString(),
        FLASK_ENV: CONFIG.isDev ? 'development' : 'production'
      },
      cwd: path.dirname(CONFIG.backendPath)
    };

    if (CONFIG.isDev) {
      // Run Python script directly in development
      backendProcess = spawn('python', [CONFIG.backendPath], options);
    } else {
      // Run compiled executable in production
      backendProcess = spawn(CONFIG.backendPath, [], options);
    }

    backendProcess.stdout.on('data', (data) => {
      log.info(`Backend: ${data.toString().trim()}`);
    });

    backendProcess.stderr.on('data', (data) => {
      log.error(`Backend Error: ${data.toString().trim()}`);
    });

    backendProcess.on('error', (error) => {
      log.error('Failed to start backend:', error);
      showErrorDialog('Backend Error', 
        `Failed to start the backend server: ${error.message}`);
    });

    backendProcess.on('close', (code) => {
      log.info(`Backend process exited with code ${code}`);
      backendProcess = null;

      if (!isQuitting && code !== 0) {
        log.warn('Backend crashed, attempting restart...');
        setTimeout(() => {
          if (!isQuitting) {
            startBackend();
          }
        }, CONFIG.restartDelay);
      }
    });

    log.info('Backend process started');
  } catch (error) {
    log.error('Error starting backend:', error);
    showErrorDialog('Startup Error', 
      `Failed to start backend: ${error.message}`);
  }
}

/**
 * Stop the backend process
 */
function stopBackend() {
  return new Promise((resolve) => {
    if (!backendProcess) {
      resolve();
      return;
    }

    log.info('Stopping backend process...');

    const timeout = setTimeout(() => {
      log.warn('Backend did not stop gracefully, forcing...');
      backendProcess.kill('SIGKILL');
      backendProcess = null;
      resolve();
    }, 5000);

    backendProcess.on('close', () => {
      clearTimeout(timeout);
      backendProcess = null;
      log.info('Backend stopped');
      resolve();
    });

    backendProcess.kill('SIGTERM');
  });
}

/**
 * Create application menu
 */
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Settings',
          accelerator: 'Ctrl+,',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.send('navigate', '/settings');
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: 'Ctrl+Q',
          click: () => {
            isQuitting = true;
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: () => {
            shell.openExternal('https://github.com/your-org/smart-hiring-system/wiki');
          }
        },
        {
          label: 'Report Issue',
          click: () => {
            shell.openExternal('https://github.com/your-org/smart-hiring-system/issues');
          }
        },
        { type: 'separator' },
        {
          label: 'About',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About Smart Hiring System',
              message: 'Smart Hiring System',
              detail: `Version: ${app.getVersion()}\n\nAI-Powered Fair Recruitment Platform\n\n© 2025 Smart Hiring System Team`,
              buttons: ['OK']
            });
          }
        }
      ]
    }
  ];

  if (CONFIG.isDev) {
    template.push({
      label: 'Developer',
      submenu: [
        { role: 'toggleDevTools' },
        { type: 'separator' },
        {
          label: 'Restart Backend',
          click: async () => {
            await stopBackend();
            startBackend();
          }
        }
      ]
    });
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

/**
 * Create system tray
 */
function createTray() {
  const iconPath = path.join(__dirname, 'assets', 'icon.ico');
  tray = new Tray(iconPath);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show App',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      }
    },
    {
      label: 'Hide App',
      click: () => {
        if (mainWindow) {
          mainWindow.hide();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip('Smart Hiring System');
  tray.setContextMenu(contextMenu);

  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

/**
 * Show error dialog
 */
function showErrorDialog(title, message) {
  dialog.showErrorBox(title, message);
}

/**
 * Configure auto-updater
 */
function setupAutoUpdater() {
  autoUpdater.logger = log;
  autoUpdater.autoDownload = false;

  autoUpdater.on('update-available', (info) => {
    log.info('Update available:', info.version);
    
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Available',
      message: `A new version (${info.version}) is available. Would you like to download it now?`,
      buttons: ['Download', 'Later']
    }).then(result => {
      if (result.response === 0) {
        autoUpdater.downloadUpdate();
      }
    });
  });

  autoUpdater.on('update-downloaded', () => {
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Ready',
      message: 'Update downloaded. The application will restart to install the update.',
      buttons: ['Restart Now', 'Later']
    }).then(result => {
      if (result.response === 0) {
        isQuitting = true;
        autoUpdater.quitAndInstall();
      }
    });
  });

  // Check for updates (only in production)
  if (!CONFIG.isDev) {
    setTimeout(() => {
      autoUpdater.checkForUpdates().catch(err => {
        log.error('Update check failed:', err);
      });
    }, 5000);
  }
}

/**
 * IPC Handlers
 */
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('get-backend-url', () => {
  return `http://${CONFIG.backendHost}:${CONFIG.backendPort}`;
});

ipcMain.handle('restart-backend', async () => {
  await stopBackend();
  startBackend();
  return { success: true };
});

ipcMain.handle('open-external', (event, url) => {
  shell.openExternal(url);
});

/**
 * App lifecycle
 */
app.whenReady().then(() => {
  log.info('App ready');
  startBackend();
  
  // Wait a bit for backend to start
  setTimeout(() => {
    createWindow();
    setupAutoUpdater();
  }, 2000);

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    } else if (mainWindow) {
      mainWindow.show();
    }
  });
});

app.on('window-all-closed', () => {
  // Keep app running in background on Windows
  if (process.platform !== 'darwin') {
    // Don't quit, just hide to tray
  }
});

app.on('before-quit', async (event) => {
  if (!isQuitting) {
    event.preventDefault();
    isQuitting = true;
    
    log.info('Application quitting...');
    await stopBackend();
    app.quit();
  }
});

app.on('will-quit', () => {
  log.info('Application will quit');
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  log.error('Uncaught exception:', error);
});

process.on('unhandledRejection', (error) => {
  log.error('Unhandled rejection:', error);
});
