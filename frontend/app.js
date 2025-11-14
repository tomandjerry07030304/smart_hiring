// Smart Hiring System - Main Application
const API_URL = 'http://localhost:5000/api';
let currentUser = null;
let currentRole = null;
let authToken = null;

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
        showDashboard(currentRole);
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
                            <input type="password" id="loginPassword" required>
                        </div>
                        <button type="submit" class="btn btn-primary btn-block">
                            <span class="btn-text">Login</span>
                            <span class="spinner"></span>
                        </button>
                        <div class="error-message"></div>
                    </form>
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
                            <label>Phone</label>
                            <input type="tel" id="regPhone">
                        </div>
                        <div class="form-group company-only" style="display: none;">
                            <label>Company Name *</label>
                            <input type="text" id="regCompany">
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label>Password *</label>
                                <input type="password" id="regPassword" required minlength="8">
                            </div>
                            <div class="form-group">
                                <label>Confirm Password *</label>
                                <input type="password" id="regConfirm" required>
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
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            localStorage.setItem('currentRole', currentRole);
            showDashboard(currentRole);
        } else {
            throw new Error(data.error || data.message || 'Login failed');
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
    switch(role) {
        case 'admin':
            loadAdminDashboard();
            break;
        case 'company':
            loadCompanyDashboard();
            break;
        case 'candidate':
            loadCandidateDashboard();
            break;
    }
}
