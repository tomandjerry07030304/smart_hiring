/**
 * Smart Hiring System - Renderer Process Entry
 * Initializes the web application and connects to backend
 */

(function() {
  'use strict';

  // Configuration
  let backendUrl = 'http://localhost:8000';
  let appVersion = 'Loading...';

  // Initialize app
  async function initializeApp() {
    try {
      // Get backend URL from main process
      if (window.electron) {
        backendUrl = await window.electron.getBackendUrl();
        appVersion = await window.electron.getAppVersion();
        
        console.log('Smart Hiring System initialized');
        console.log('Version:', appVersion);
        console.log('Backend URL:', backendUrl);
        
        // Display app info
        displayAppInfo();
        
        // Check backend health
        checkBackendHealth();
      }
    } catch (error) {
      console.error('Initialization error:', error);
      showError('Failed to initialize application', error.message);
    }
  }

  // Display app information
  function displayAppInfo() {
    const infoDiv = document.getElementById('app-info');
    if (infoDiv) {
      infoDiv.innerHTML = `
        <div class="app-info">
          <h1>Smart Hiring System</h1>
          <p>Version: ${appVersion}</p>
          <p>Backend: ${backendUrl}</p>
        </div>
      `;
    }
  }

  // Check backend health
  async function checkBackendHealth() {
    const statusDiv = document.getElementById('backend-status');
    if (!statusDiv) return;

    try {
      const response = await fetch(`${backendUrl}/api/health`);
      const data = await response.json();
      
      if (data.status === 'healthy') {
        statusDiv.innerHTML = `
          <div class="status-success">
            <span class="status-indicator"></span>
            Backend: Connected
          </div>
        `;
        
        // Backend is ready, load main application
        loadApplication();
      } else {
        throw new Error('Backend unhealthy');
      }
    } catch (error) {
      statusDiv.innerHTML = `
        <div class="status-error">
          <span class="status-indicator"></span>
          Backend: Disconnected
          <button onclick="retryConnection()">Retry</button>
        </div>
      `;
      console.error('Backend health check failed:', error);
    }
  }

  // Load main application
  function loadApplication() {
    console.log('Loading main application...');
    
    // This will be replaced by React app loading
    // For now, just redirect to backend
    const appContainer = document.getElementById('app-container');
    if (appContainer) {
      appContainer.innerHTML = `
        <iframe 
          src="${backendUrl}" 
          style="width: 100%; height: 100vh; border: none;"
          title="Smart Hiring System"
        ></iframe>
      `;
    } else {
      // If no container, just navigate
      window.location.href = backendUrl;
    }
  }

  // Show error message
  function showError(title, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
      <h2>${title}</h2>
      <p>${message}</p>
      <button onclick="location.reload()">Reload</button>
    `;
    document.body.appendChild(errorDiv);
  }

  // Retry connection
  window.retryConnection = function() {
    checkBackendHealth();
  };

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
  } else {
    initializeApp();
  }

  // Handle navigation events from main process
  if (window.electron) {
    window.electron.onNavigate((route) => {
      console.log('Navigating to:', route);
      // Handle navigation when React is implemented
    });
  }

})();
