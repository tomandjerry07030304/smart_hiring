// Company Dashboard Module
function loadCompanyDashboard() {
    const dashboard = document.getElementById('companyDashboard');
    dashboard.innerHTML = `
        <nav class="navbar">
            <div class="navbar-brand">
                <svg width="32" height="32" viewBox="0 0 64 64">
                    <circle cx="32" cy="32" r="30" fill="#4F46E5"/>
                    <path d="M32 16L40 28H24L32 16Z" fill="white"/>
                    <rect x="22" y="30" width="20" height="18" rx="2" fill="white"/>
                </svg>
                <span>Company Portal</span>
            </div>
            <div class="navbar-menu">
                <button class="nav-link active" onclick="switchCompanyTab('overview')">📊 Dashboard</button>
                <button class="nav-link" onclick="switchCompanyTab('jobs')">💼 My Jobs</button>
                <button class="nav-link" onclick="switchCompanyTab('candidates')">🎯 Candidates</button>
                <button class="nav-link" onclick="switchCompanyTab('applications')">📋 Applications</button>
            </div>
            <div class="navbar-actions">
                <span class="user-info">${currentUser.email}</span>
                <button class="btn btn-secondary" onclick="companyLogout()">Logout</button>
            </div>
        </nav>
        <div class="main-content">
            <div id="companyOverview" class="tab-content active"></div>
            <div id="companyJobs" class="tab-content"></div>
            <div id="companyCandidates" class="tab-content"></div>
            <div id="companyApplications" class="tab-content"></div>
        </div>
    `;
    showPage('companyDashboard');
    loadCompanyOverview();
}

function switchCompanyTab(tab) {
    document.querySelectorAll('#companyDashboard .nav-link').forEach(l => l.classList.remove('active'));
    document.querySelectorAll('#companyDashboard .tab-content').forEach(t => t.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(`company${tab.charAt(0).toUpperCase() + tab.slice(1)}`).classList.add('active');
    
    switch(tab) {
        case 'overview': loadCompanyOverview(); break;
        case 'jobs': loadCompanyJobs(); break;
        case 'candidates': loadCompanyCandidates(); break;
        case 'applications': loadCompanyApplications(); break;
    }
}

async function loadCompanyOverview() {
    const container = document.getElementById('companyOverview');
    container.innerHTML = '<div class="loading">Loading dashboard...</div>';
    
    try {
        const response = await fetch(`${API_URL}/dashboard/company`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        container.innerHTML = `
            <div class="content-header">
                <h2>📊 Company Dashboard</h2>
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">💼</div>
                    <div class="stat-content">
                        <div class="stat-label">Active Jobs</div>
                        <div class="stat-value">${data.active_jobs || 0}</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📋</div>
                    <div class="stat-content">
                        <div class="stat-label">Applications</div>
                        <div class="stat-value">${data.total_applications || 0}</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">👥</div>
                    <div class="stat-content">
                        <div class="stat-label">Matched Candidates</div>
                        <div class="stat-value">${data.matched_candidates || 0}</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📅</div>
                    <div class="stat-content">
                        <div class="stat-label">Interviews Scheduled</div>
                        <div class="stat-value">${data.interviews_scheduled || 0}</div>
                    </div>
                </div>
            </div>
            <div class="card">
                <h3>🎯 Quick Actions</h3>
                <p>Start by posting a job to receive qualified candidate matches based on their assessment scores.</p>
                <button class="btn btn-primary" onclick="switchCompanyTab('jobs')">Post a Job</button>
            </div>
        `;
    } catch (error) {
        container.innerHTML = '<div class="empty-state">Failed to load dashboard</div>';
    }
}

async function loadCompanyJobs() {
    const container = document.getElementById('companyJobs');
    container.innerHTML = '<div class="loading">Loading jobs...</div>';
    
    try {
        const response = await fetch(`${API_URL}/jobs/company`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        const jobs = data.jobs || [];
        
        container.innerHTML = `
            <div class="content-header">
                <h2>💼 My Job Postings</h2>
                <button class="btn btn-primary" onclick="showJobModal()">+ Post New Job</button>
            </div>
            ${jobs.length === 0 ? 
                '<div class="empty-state">No jobs posted yet. Click "Post New Job" to get started!</div>' :
                `<div class="job-grid">
                    ${jobs.map(job => `
                        <div class="job-card" onclick="viewJobDetails('${job._id}')">
                            <div class="job-header">
                                <div>
                                    <h3 class="job-title">${job.title}</h3>
                                    <p class="job-company">${job.department}</p>
                                </div>
                                <span class="badge badge-${job.status === 'active' ? 'success' : 'warning'}">
                                    ${job.status}
                                </span>
                            </div>
                            <p class="job-description">${job.description.substring(0, 150)}...</p>
                            <div class="job-meta">
                                <span>📍 ${job.location}</span>
                                <span>💼 ${job.job_type}</span>
                                <span>📋 ${job.applications_count || 0} applications</span>
                            </div>
                            <div class="job-tags">
                                ${(job.required_skills || []).slice(0, 5).map(s => `<span class="tag">${s}</span>`).join('')}
                            </div>
                            <button class="btn btn-primary" onclick="event.stopPropagation(); viewJobCandidates('${job._id}')">
                                View Candidates
                            </button>
                        </div>
                    `).join('')}
                </div>`
            }
        `;
    } catch (error) {
        container.innerHTML = '<div class="empty-state">Failed to load jobs</div>';
    }
}

function showJobModal() {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">Post New Job</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
            </div>
            <form onsubmit="submitJob(event)">
                <div class="modal-body">
                    <div class="form-group">
                        <label>Job Title *</label>
                        <input type="text" id="jobTitle" required>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Department *</label>
                            <input type="text" id="jobDepartment" required>
                        </div>
                        <div class="form-group">
                            <label>Location *</label>
                            <input type="text" id="jobLocation" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Job Type *</label>
                        <select id="jobType" required>
                            <option value="full-time">Full-time</option>
                            <option value="part-time">Part-time</option>
                            <option value="contract">Contract</option>
                            <option value="internship">Internship</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Description *</label>
                        <textarea id="jobDescription" required></textarea>
                    </div>
                    <div class="form-group">
                        <label>Requirements *</label>
                        <textarea id="jobRequirements" required placeholder="One requirement per line"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Required Skills *</label>
                        <input type="text" id="jobSkills" required placeholder="Comma-separated (e.g., Python, JavaScript, React)">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Post Job</button>
                </div>
            </form>
        </div>
    `;
    document.body.appendChild(modal);
}

async function submitJob(e) {
    e.preventDefault();
    
    const jobData = {
        title: document.getElementById('jobTitle').value,
        department: document.getElementById('jobDepartment').value,
        location: document.getElementById('jobLocation').value,
        job_type: document.getElementById('jobType').value,
        description: document.getElementById('jobDescription').value,
        requirements: document.getElementById('jobRequirements').value.split('\n').filter(r => r.trim()),
        required_skills: document.getElementById('jobSkills').value.split(',').map(s => s.trim())
    };
    
    try {
        const response = await fetch(`${API_URL}/jobs/create`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jobData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✓ Job posted successfully!');
            e.target.closest('.modal').remove();
            loadCompanyJobs();
        } else {
            alert('Failed to post job: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error posting job:', error);
        alert('Failed to post job: ' + error.message);
    }
}

async function loadCompanyCandidates() {
    const container = document.getElementById('companyCandidates');
    container.innerHTML = `
        <div class="content-header">
            <h2>🎯 Matched Candidates</h2>
        </div>
        <div class="card">
            <p>View candidates matched to your job postings based on their assessment scores and skills.</p>
            <p class="empty-state">Post jobs to see matched candidates</p>
        </div>
    `;
}

async function loadCompanyApplications() {
    const container = document.getElementById('companyApplications');
    container.innerHTML = '<div class="loading">Loading applications...</div>';
    
    try {
        const response = await fetch(`${API_URL}/applications/company`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        const applications = data.applications || [];
        
        if (applications.length === 0) {
            container.innerHTML = '<div class="empty-state">No applications yet</div>';
            return;
        }
        
        container.innerHTML = `
            <div class="content-header">
                <h2>📋 Applications</h2>
            </div>
            <div class="job-grid">
                ${applications.map(app => `
                    <div class="job-card">
                        <h3 class="job-title">${app.candidate_name}</h3>
                        <p class="job-company">Applied for: ${app.job_title}</p>
                        <div class="job-meta">
                            <span>📅 ${new Date(app.applied_at).toLocaleDateString()}</span>
                            <span class="badge badge-info">${app.status}</span>
                        </div>
                        <button class="btn btn-primary" onclick="reviewApplication('${app._id}')">Review Application</button>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        container.innerHTML = '<div class="empty-state">Failed to load applications</div>';
    }
}

function companyLogout() {
    // Clear authentication data
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('currentRole');
    
    // Reload the page to return to login
    window.location.href = '/';
}
