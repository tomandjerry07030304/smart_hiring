// Smart Hiring System - Main Application
// Auto-detect API URL based on environment
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000/api'
    : window.location.origin + '/api';  // Use same domain for production
let currentUser = null;
let currentRole = null;
let authToken = null;

// Toggle password visibility
function togglePasswordVisibility(inputId, button) {
    const input = document.getElementById(inputId);
    const eyeIcon = button.querySelector('.eye-icon');
    const eyeOffIcon = button.querySelector('.eye-off-icon');
    
    if (input.type === 'password') {
        input.type = 'text';
        eyeIcon.style.display = 'none';
        eyeOffIcon.style.display = 'block';
    } else {
        input.type = 'password';
        eyeIcon.style.display = 'block';
        eyeOffIcon.style.display = 'none';
    }
}

// Modern Notification System
function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notification-container');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ',
        warning: '⚠'
    };
    
    notification.innerHTML = `
        <span class="notification-icon">${icons[type] || icons.info}</span>
        <div class="notification-content">
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    checkAuth();
});

function checkAuth() {
    authToken = localStorage.getItem('authToken');
    currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    currentRole = localStorage.getItem('currentRole');
    
    if (authToken && currentUser && currentRole) {
        // Validate that the stored role matches the user's actual role
        if (currentUser.role && currentUser.role !== currentRole) {
            console.warn('Role mismatch detected. Correcting...');
            currentRole = currentUser.role;
            localStorage.setItem('currentRole', currentRole);
        }
        showDashboard(currentUser.role || currentRole);
    } else {
        showRoleSelection();
    }
}

function initializeApp() {
    const app = document.getElementById('app');
    app.innerHTML = `
        <!-- Role Selection Page -->
        <div id="roleSelectionPage" class="page active">
            <div class="role-selection">
                <div class="role-container">
                    <div class="role-header">
                        <div class="logo-large">
                            <svg width="80" height="80" viewBox="0 0 64 64">
                                <circle cx="32" cy="32" r="30" fill="#4F46E5"/>
                                <path d="M32 16L40 28H24L32 16Z" fill="white"/>
                                <rect x="22" y="30" width="20" height="18" rx="2" fill="white"/>
                            </svg>
                        </div>
                        <h1>Smart Hiring System</h1>
                        <p class="subtitle">AI-Powered Fair Recruitment Platform</p>
                        <p>We connect companies with qualified candidates through intelligent assessments</p>
                    </div>
                    <div class="role-cards">
                        <div class="role-card">
                            <div class="role-icon">👨‍💼</div>
                            <h3>Platform Admin</h3>
                            <p>Manage platform, oversee operations, and configure assessments</p>
                            <button class="btn btn-primary btn-block" onclick="selectRole('admin')">Admin Portal</button>
                        </div>
                        <div class="role-card">
                            <div class="role-icon">🏢</div>
                            <h3>Company / Recruiter</h3>
                            <p>Post jobs, review candidates, and manage hiring process</p>
                            <button class="btn btn-primary btn-block" onclick="selectRole('company')">Company Portal</button>
                        </div>
                        <div class="role-card">
                            <div class="role-icon">👨‍💻</div>
                            <h3>Job Seeker</h3>
                            <p>Browse jobs, take assessments, and track applications</p>
                            <button class="btn btn-primary btn-block" onclick="selectRole('candidate')">Candidate Portal</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Login Page -->
        <div id="loginPage" class="page">
            <div class="auth-container">
                <div class="auth-card">
                    <button class="back-btn" onclick="showRoleSelection()">← Back</button>
                    
                    <div class="logo">
                        <svg width="64" height="64" viewBox="0 0 64 64">
                            <circle cx="32" cy="32" r="30" fill="#4F46E5"/>
                            <path d="M32 16L40 28H24L32 16Z" fill="white"/>
                            <rect x="22" y="30" width="20" height="18" rx="2" fill="white"/>
                        </svg>
                    </div>
                    
                    <h1 id="loginTitle">Login</h1>
                    <p class="subtitle" id="loginSubtitle"></p>
                    <form id="loginForm" onsubmit="handleLogin(event)">
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" id="loginEmail" required>
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <div class="password-input-wrapper">
                                <input type="password" id="loginPassword" required>
                                <button type="button" class="password-toggle" onclick="togglePasswordVisibility('loginPassword', this)" aria-label="Toggle password visibility">
                                    <svg class="eye-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                        <circle cx="12" cy="12" r="3"></circle>
                                    </svg>
                                    <svg class="eye-off-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none;">
                                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                                        <line x1="1" y1="1" x2="23" y2="23"></line>
                                    </svg>
                                </button>
                            </div>
                        </div>
                        <div class="forgot-password-link">
                            <a href="forgot-password.html">Forgot Password?</a>
                        </div>
                        <button type="submit" class="btn btn-primary btn-block">
                            <span class="btn-text">Login</span>
                            <span class="spinner"></span>
                        </button>
                        <div class="error-message"></div>
                    </form>
                    
                    <!-- Google Sign-In Section (Only for Candidates) -->
                    <div id="googleSignInSection" class="social-login-section" style="display: none;">
                        <div class="divider">
                            <span>OR</span>
                        </div>
                        <button type="button" class="btn btn-google" onclick="handleGoogleSignIn()">
                            <svg width="20" height="20" viewBox="0 0 24 24">
                                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                            </svg>
                            <span>Sign in with Google</span>
                        </button>
                    </div>
                    
                    <div class="auth-footer">
                        <p id="registerPrompt">Don't have an account? <a href="#" onclick="showRegister(); return false;">Register here</a></p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Register Page -->
        <div id="registerPage" class="page">
            <div class="auth-container">
                <div class="auth-card">
                    <button class="back-btn" onclick="showLogin()">← Back to Login</button>
                    <div class="logo">
                        <svg width="64" height="64" viewBox="0 0 64 64">
                            <circle cx="32" cy="32" r="30" fill="#4F46E5"/>
                            <path d="M32 16L40 28H24L32 16Z" fill="white"/>
                            <rect x="22" y="30" width="20" height="18" rx="2" fill="white"/>
                        </svg>
                    </div>
                    <h1 id="registerTitle">Create Account</h1>
                    <p class="subtitle" id="registerSubtitle"></p>
                    <form id="registerForm" onsubmit="handleRegister(event)">
                        <div class="form-row">
                            <div class="form-group">
                                <label>First Name *</label>
                                <input type="text" id="regFirstName" required>
                            </div>
                            <div class="form-group">
                                <label>Last Name *</label>
                                <input type="text" id="regLastName" required>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Email *</label>
                            <input type="email" id="regEmail" required>
                        </div>
                        <div class="form-group">
                            <label>Phone Number</label>
                            <div style="display: flex; gap: 8px;">
                                <select id="regCountryCode" style="width: 140px;">
                                    <option value="+1">🇺🇸 +1 (US)</option>
                                    <option value="+44">🇬🇧 +44 (UK)</option>
                                    <option value="+91" selected>🇮🇳 +91 (India)</option>
                                    <option value="+61">🇦🇺 +61 (Australia)</option>
                                    <option value="+81">🇯🇵 +81 (Japan)</option>
                                    <option value="+86">🇨🇳 +86 (China)</option>
                                    <option value="+49">🇩🇪 +49 (Germany)</option>
                                    <option value="+33">🇫🇷 +33 (France)</option>
                                    <option value="+39">🇮🇹 +39 (Italy)</option>
                                    <option value="+34">🇪🇸 +34 (Spain)</option>
                                    <option value="+7">🇷🇺 +7 (Russia)</option>
                                    <option value="+55">🇧🇷 +55 (Brazil)</option>
                                    <option value="+52">🇲🇽 +52 (Mexico)</option>
                                    <option value="+27">🇿🇦 +27 (S. Africa)</option>
                                    <option value="+82">🇰🇷 +82 (S. Korea)</option>
                                    <option value="+65">🇸🇬 +65 (Singapore)</option>
                                </select>
                                <input type="tel" id="regPhone" placeholder="1234567890" style="flex: 1;">
                            </div>
                        </div>
                        <div class="form-group company-only" style="display: none;">
                            <label>Company Name *</label>
                            <input type="text" id="regCompany">
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label>Password *</label>
                                <div class="password-input-wrapper">
                                    <input type="password" id="regPassword" required minlength="8">
                                    <button type="button" class="password-toggle" onclick="togglePasswordVisibility('regPassword', this)" aria-label="Toggle password visibility">
                                        <svg class="eye-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                            <circle cx="12" cy="12" r="3"></circle>
                                        </svg>
                                        <svg class="eye-off-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none;">
                                            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                                            <line x1="1" y1="1" x2="23" y2="23"></line>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Confirm Password *</label>
                                <div class="password-input-wrapper">
                                    <input type="password" id="regConfirm" required>
                                    <button type="button" class="password-toggle" onclick="togglePasswordVisibility('regConfirm', this)" aria-label="Toggle password visibility">
                                        <svg class="eye-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                            <circle cx="12" cy="12" r="3"></circle>
                                        </svg>
                                        <svg class="eye-off-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none;">
                                            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                                            <line x1="1" y1="1" x2="23" y2="23"></line>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary btn-block">
                            <span class="btn-text">Create Account</span>
                            <span class="spinner"></span>
                        </button>
                        <div class="error-message"></div>
                        <div class="success-message"></div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Admin Dashboard -->
        <div id="adminDashboard" class="page"></div>

        <!-- Company Dashboard -->
        <div id="companyDashboard" class="page"></div>

        <!-- Candidate Dashboard -->
        <div id="candidateDashboard" class="page"></div>
    `;
}

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
}

function showRoleSelection() {
    showPage('roleSelectionPage');
}

function selectRole(role) {
    currentRole = role;
    const titles = {
        admin: 'Admin Login',
        company: 'Company Login',
        candidate: 'Candidate Login'
    };
    const subtitles = {
        admin: 'Platform Administrator Access',
        company: 'Recruiter & Company Portal',
        candidate: 'Job Seeker Portal'
    };
    document.getElementById('loginTitle').textContent = titles[role];
    document.getElementById('loginSubtitle').textContent = subtitles[role];
    
    if (role === 'admin') {
        document.getElementById('registerPrompt').style.display = 'none';
    } else {
        document.getElementById('registerPrompt').style.display = 'block';
    }
    
    // Show Google Sign-In only for candidates
    const googleSection = document.getElementById('googleSignInSection');
    if (googleSection) {
        googleSection.style.display = role === 'candidate' ? 'block' : 'none';
    }
    
    showPage('loginPage');
}

function showLogin() {
    showPage('loginPage');
}

function showRegister() {
    const titles = {
        company: 'Company Registration',
        candidate: 'Candidate Registration'
    };
    const subtitles = {
        company: 'Register your company to start hiring',
        candidate: 'Create your profile to find jobs'
    };
    
    document.getElementById('registerTitle').textContent = titles[currentRole];
    document.getElementById('registerSubtitle').textContent = subtitles[currentRole];
    
    if (currentRole === 'company') {
        document.querySelector('.company-only').style.display = 'block';
        document.getElementById('regCompany').required = true;
    }
    
    showPage('registerPage');
}

// Google Sign-In Handler
// Google Sign-In Handler (FIXED)
async function handleGoogleSignIn() {
    try {
        // Check if Google OAuth is configured
        const statusResponse = await fetch(`${API_URL}/auth/google/status`);
        const statusData = await statusResponse.json();

        if (!statusData.google_oauth_available) {
            showNotification(
                'Google Sign-In is not configured yet. Please use email/password login.',
                'warning'
            );
            return;
        }

        // Get Google Auth URL
        const response = await fetch(`${API_URL}/auth/google/login`);
        const data = await response.json();

        if (data.auth_url) {
            // Redirect to Google for authentication
            window.location.href = data.auth_url;
        } else {
            showNotification(
                'Failed to initialize Google Sign-In. Please try again.',
                'error'
            );
        }
    } catch (error) {
        console.error('Google Sign-In error:', error);
        showNotification(
            'Google Sign-In is currently unavailable. Please use email/password login.',
            'error'
        );
    }
}

/*async function handleGoogleSignIn() {
    try {
        // Check if Google OAuth is configured
        const statusResponse = await fetch(`${API_BASE}/api/auth/google/status`);
        const statusData = await statusResponse.json();
        
        if (!statusData.configured) {
            showNotification('Google Sign-In is not configured yet. Please use email/password login.', 'warning');
            return;
        }
        
        // Get Google Auth URL
        const response = await fetch(`${API_BASE}/api/auth/google/login`);
        const data = await response.json();
        
        if (data.auth_url) {
            // Redirect to Google for authentication
            window.location.href = data.auth_url;
        } else {
            showNotification('Failed to initialize Google Sign-In. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Google Sign-In error:', error);
        showNotification('Google Sign-In is currently unavailable. Please use email/password login.', 'error');
    }
}*/

async function handleLogin(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const btnText = btn.querySelector('.btn-text');
    const spinner = btn.querySelector('.spinner');
    const errorDiv = e.target.querySelector('.error-message');
    
    btn.disabled = true;
    btnText.style.display = 'none';
    spinner.classList.add('show');
    errorDiv.classList.remove('show');
    
    try {
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, role: currentRole })
        });
        
        // Check if response is OK before trying to parse JSON
        if (!response.ok) {
            // Try to parse error message, but handle non-JSON responses
            let errorMessage = 'Login failed. Please try again.';
            try {
                const data = await response.json();
                errorMessage = data.error || data.message || errorMessage;
            } catch (jsonError) {
                // If JSON parsing fails, use status-based message
                if (response.status === 502) {
                    errorMessage = 'Service temporarily unavailable. Please try again in a moment.';
                } else if (response.status === 500) {
                    errorMessage = 'Server error. Please contact support.';
                }
            }
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        authToken = data.access_token;
        currentUser = data.user;
        
        // Use the actual role from the database, not the selected portal
        const actualRole = data.user.role;
        
        // Normalize roles: 'recruiter' and 'company' are interchangeable
        const normalizedActualRole = actualRole === 'recruiter' ? 'company' : actualRole;
        const normalizedCurrentRole = currentRole === 'recruiter' ? 'company' : currentRole;
        
        // Validate role matches selected portal (optional strict check)
        if (normalizedCurrentRole !== 'admin' && normalizedActualRole !== normalizedCurrentRole && normalizedActualRole !== 'admin') {
            throw new Error(`This account is registered as ${actualRole}. Please use the ${actualRole} portal.`);
        }
        
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        localStorage.setItem('currentRole', actualRole);  // Save actual role
        showDashboard(actualRole);
    } catch (error) {
        console.error('Login error:', error);
        errorDiv.textContent = error.message || 'An unexpected error occurred';
        errorDiv.classList.add('show');
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline';
        spinner.classList.remove('show');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const btnText = btn.querySelector('.btn-text');
    const spinner = btn.querySelector('.spinner');
    const errorDiv = e.target.querySelector('.error-message');
    const successDiv = e.target.querySelector('.success-message');
    
    const password = document.getElementById('regPassword').value;
    const confirm = document.getElementById('regConfirm').value;
    
    if (password !== confirm) {
        errorDiv.textContent = 'Passwords do not match';
        errorDiv.classList.add('show');
        return;
    }
    
    btn.disabled = true;
    btnText.style.display = 'none';
    spinner.classList.add('show');
    errorDiv.classList.remove('show');
    successDiv.classList.remove('show');
    
    try {
        const firstName = document.getElementById('regFirstName').value;
        const lastName = document.getElementById('regLastName').value;
        
        const userData = {
            full_name: `${firstName} ${lastName}`,
            email: document.getElementById('regEmail').value,
            phone: document.getElementById('regPhone').value,
            password: password,
            role: currentRole === 'company' ? 'recruiter' : currentRole
        };
        
        if (currentRole === 'company') {
            userData.company_name = document.getElementById('regCompany').value;
        }
        
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            successDiv.textContent = 'Registration successful! Redirecting to login...';
            successDiv.classList.add('show');
            e.target.reset();
            setTimeout(() => showLogin(), 2000);
        } else {
            throw new Error(data.error || data.message || 'Registration failed');
        }
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.classList.add('show');
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline';
        spinner.classList.remove('show');
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    currentRole = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('currentRole');
    showRoleSelection();
}

function showDashboard(role) {
    // Ensure role matches the logged-in user's role
    const userRole = currentUser?.role || role;
    
    // Redirect if trying to access wrong portal
    if (userRole !== role) {
        console.warn(`Access denied: User role is ${userRole}, attempting to access ${role} portal`);
        role = userRole;
    }
    
    switch(role) {
        case 'admin':
            loadAdminDashboard();
            break;
        case 'company':
        case 'recruiter':
            loadCompanyDashboard();
            break;
        case 'candidate':
            loadCandidateDashboard();
            break;
        default:
            console.error('Unknown role:', role);
            logout();
    }
}

function loadAdminDashboard() {
    console.log('Loading Admin Dashboard...');
    document.getElementById('authPage').style.display = 'none';
    document.body.innerHTML = `
        <div style="padding: 40px; max-width: 1200px; margin: 0 auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
                <h1 style="color: #4F46E5;">Admin Dashboard</h1>
                <button onclick="logout()" style="padding: 10px 20px; background: #ef4444; color: white; border: none; border-radius: 8px; cursor: pointer;">Logout</button>
            </div>
            <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2>Welcome, ${currentUser.full_name}!</h2>
                <p style="color: #6b7280; margin-top: 10px;">Email: ${currentUser.email}</p>
                <p style="color: #6b7280;">Role: Administrator</p>
                <div style="margin-top: 30px; padding: 20px; background: #f3f4f6; border-radius: 8px;">
                    <h3>🎉 Deployment Successful!</h3>
                    <p style="margin-top: 10px;">Your Smart Hiring System is now live on Render.com</p>
                    <p style="margin-top: 10px; color: #6b7280; font-size: 14px;">
                        <strong>Note:</strong> Some features are temporarily disabled due to deployment size constraints:
                    </p>
                    <ul style="margin-top: 10px; color: #6b7280; font-size: 14px;">
                        <li>✓ Authentication System - Active</li>
                        <li>✓ Job Management - Active</li>
                        <li>✓ Candidate Management - Active</li>
                        <li>⚠ Assessment System - Disabled (ML libraries removed)</li>
                        <li>⚠ Dashboard Analytics - Disabled (pandas removed)</li>
                        <li>⚠ PDF/DOCX Resume Parsing - Disabled (size constraints)</li>
                    </ul>
                </div>
            </div>
        </div>
    `;
}

function loadCompanyDashboard() {
    console.log('Loading Company Dashboard...');
    document.getElementById('authPage').style.display = 'none';
    document.body.innerHTML = `
        <div style="padding: 40px; max-width: 1200px; margin: 0 auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
                <h1 style="color: #4F46E5;">Company Dashboard</h1>
                <button onclick="logout()" style="padding: 10px 20px; background: #ef4444; color: white; border: none; border-radius: 8px; cursor: pointer;">Logout</button>
            </div>
            <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2>Welcome, ${currentUser.full_name}!</h2>
                <p style="color: #6b7280; margin-top: 10px;">Email: ${currentUser.email}</p>
                <p style="color: #6b7280;">Role: Recruiter</p>
                <div style="margin-top: 30px;">
                    <h3>Company Dashboard Features Coming Soon</h3>
                    <ul style="margin-top: 15px; color: #6b7280;">
                        <li>Post and manage job openings</li>
                        <li>Review candidate applications</li>
                        <li>Schedule interviews</li>
                        <li>Track hiring pipeline</li>
                    </ul>
                </div>
            </div>
        </div>
    `;
}

function loadCandidateDashboard() {
    console.log('Loading Candidate Dashboard...');
    document.getElementById('authPage').style.display = 'none';
    document.body.innerHTML = `
        <div style="padding: 40px; max-width: 1200px; margin: 0 auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
                <h1 style="color: #4F46E5;">Candidate Dashboard</h1>
                <button onclick="logout()" style="padding: 10px 20px; background: #ef4444; color: white; border: none; border-radius: 8px; cursor: pointer;">Logout</button>
            </div>
            <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2>Welcome, ${currentUser.full_name}!</h2>
                <p style="color: #6b7280; margin-top: 10px;">Email: ${currentUser.email}</p>
                <p style="color: #6b7280;">Role: Candidate</p>
                <div style="margin-top: 30px;">
                    <h3>Candidate Dashboard Features Coming Soon</h3>
                    <ul style="margin-top: 15px; color: #6b7280;">
                        <li>Browse available jobs</li>
                        <li>Submit applications</li>
                        <li>Track application status</li>
                        <li>Take assessments</li>
                        <li>Upload and manage resume</li>
                    </ul>
                </div>
            </div>
        </div>
    `;
}
