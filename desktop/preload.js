/**
 * Smart Hiring System - Electron Preload Script
 * Exposes secure APIs to the renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electron', {
  // App information
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
  
  // Backend control
  restartBackend: () => ipcRenderer.invoke('restart-backend'),
  
  // External links
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  
  // Navigation
  onNavigate: (callback) => {
    ipcRenderer.on('navigate', (event, route) => callback(route));
  },
  
  // Platform information
  platform: process.platform,
  isDev: process.argv.includes('--dev')
});

// Log preload completion
console.log('Preload script loaded');
