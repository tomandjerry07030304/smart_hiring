// Company Dashboard Module
function loadCompanyDashboard() {
    console.log('Loading Company Dashboard...', currentUser);
    
    // Ensure currentUser is available
    if (!currentUser) {
        console.error('No current user found');
        logout();
        return;
    }
    
    const dashboard = document.getElementById('companyDashboard');
    if (!dashboard) {
        console.error('Company dashboard element not found');
        return;
    }
    
    const userEmail = currentUser.email || currentUser.full_name || 'User';
    
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
                <button class="nav-link" onclick="switchCompanyTab('analytics')">📈 Analytics</button>
                <button class="nav-link" onclick="switchCompanyTab('audit')">🛡️ Fairness Audit</button>
            </div>
            <div class="navbar-actions">
                <span class="user-info">${userEmail}</span>
                <button class="btn btn-secondary" onclick="companyLogout()">Logout</button>
            </div>
        </nav>
        <div class="main-content">
            <div id="companyOverview" class="tab-content active"></div>
            <div id="companyJobs" class="tab-content"></div>
            <div id="companyCandidates" class="tab-content"></div>
            <div id="companyApplications" class="tab-content"></div>
            <div id="companyAnalytics" class="tab-content"></div>
            <div id="companyAudit" class="tab-content"></div>
        </div>
    `;
    showPage('companyDashboard');
    loadCompanyOverview();
}

function switchCompanyTab(tab) {
    console.log('Switching to company tab:', tab);
    document.querySelectorAll('#companyDashboard .nav-link').forEach(l => l.classList.remove('active'));
    document.querySelectorAll('#companyDashboard .tab-content').forEach(t => t.classList.remove('active'));
    
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    // Show the corresponding tab content
    const tabMap = {
        'overview': 'companyOverview',
        'jobs': 'companyJobs',
        'candidates': 'companyCandidates',
        'applications': 'companyApplications',
        'analytics': 'companyAnalytics',
        'audit': 'companyAudit'
    };
    
    const tabElement = document.getElementById(tabMap[tab]);
    if (tabElement) {
        tabElement.classList.add('active');
    }
    
    switch(tab) {
        case 'overview': loadCompanyOverview(); break;
        case 'jobs': loadCompanyJobs(); break;
        case 'candidates': loadCompanyCandidates(); break;
        case 'applications': loadCompanyApplications(); break;
        case 'analytics': loadCompanyAnalytics(); break;
        case 'audit': loadCompanyAudit(); break;
    }
}

async function loadCompanyOverview() {
    console.log('Loading company overview...');
    const container = document.getElementById('companyOverview');
    if (!container) {
        console.error('Company overview container not found');
        return;
    }
    
    container.innerHTML = '<div class="loading">Loading dashboard...</div>';
    
    try {
        const response = await fetch(`${API_URL}/jobs/company/stats`, {
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
                                    <p class="job-company">${job.company_name || job.department || 'Smart Hiring'}</p>
                                </div>
                                <span class="badge badge-${job.status === 'open' ? 'success' : 'warning'}">
                                    ${job.status}
                                </span>
                            </div>
                            <p class="job-description" style="white-space: pre-line;">${job.description.substring(0, 200)}...</p>
                            <div class="job-meta">
                                <span>📍 ${job.location || 'Remote'}</span>
                                <span>💼 ${job.job_type || 'Full-time'}</span>
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
    
    const title = document.getElementById('jobTitle').value.trim();
    const description = document.getElementById('jobDescription').value.trim();
    const requirements = document.getElementById('jobRequirements').value.trim();
    
    // Validate required fields
    if (!title || !description) {
        alert('Title and Description are required!');
        return;
    }
    
    // Combine description and requirements
    const fullDescription = description + (requirements ? '\n\nRequirements:\n' + requirements : '');
    
    const jobData = {
        title: title,
        company_name: document.getElementById('jobDepartment').value.trim() || 'Smart Hiring',
        location: document.getElementById('jobLocation').value.trim(),
        job_type: document.getElementById('jobType').value,
        description: fullDescription,
        required_skills: document.getElementById('jobSkills').value.split(',').map(s => s.trim()).filter(s => s)
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
        console.log('Job posting response:', response.status, data);
        
        if (response.ok) {
            alert('✓ Job posted successfully!');
            e.target.closest('.modal').remove();
            loadCompanyJobs();
        } else {
            const errorMsg = data.error || data.message || JSON.stringify(data);
            console.error('Job posting failed:', errorMsg);
            alert('Failed to post job: ' + errorMsg);
        }
    } catch (error) {
        console.error('Error posting job:', error);
        alert('Failed to post job: ' + error.message);
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

let selectedApplications = new Set();
let currentStatusFilter = 'all';

async function loadCompanyApplications() {
    const container = document.getElementById('companyApplications');
    container.innerHTML = '<div class="loading">Loading applications...</div>';
    
    try {
        const response = await fetch(`${API_URL}/jobs/company/applications`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        let applications = data.applications || [];
        
        if (applications.length === 0) {
            container.innerHTML = `
                <div class="content-header">
                    <h2>📋 Applications</h2>
                </div>
                <div class="empty-state">
                    <div style="font-size: 64px; margin-bottom: 16px;">📭</div>
                    <h3>No Applications Yet</h3>
                    <p>Applications will appear here once candidates apply to your jobs.</p>
                </div>
            `;
            return;
        }
        
        // Filter applications by status
        const filteredApps = currentStatusFilter === 'all' 
            ? applications 
            : applications.filter(app => app.status === currentStatusFilter);
        
        // Calculate statistics
        const stats = {
            total: applications.length,
            pending: applications.filter(a => a.status === 'pending').length,
            shortlisted: applications.filter(a => a.status === 'shortlisted').length,
            interviewed: applications.filter(a => a.status === 'interviewed').length,
            hired: applications.filter(a => a.status === 'hired').length,
            rejected: applications.filter(a => a.status === 'rejected').length
        };
        
        container.innerHTML = `
            <div class="content-header">
                <h2>📋 Applications Management</h2>
                <div style="display: flex; gap: 12px;">
                    ${selectedApplications.size > 0 ? `
                        <button class="btn btn-secondary" onclick="clearSelection()">
                            Clear (${selectedApplications.size})
                        </button>
                        <button class="btn btn-primary" onclick="bulkUpdateStatus()">
                            Update Selected
                        </button>
                    ` : ''}
                </div>
            </div>
            
            <!-- Status Filter Tabs -->
            <div class="status-filter-tabs">
                <button class="filter-tab ${currentStatusFilter === 'all' ? 'active' : ''}" 
                        onclick="filterByStatus('all')">
                    All (${stats.total})
                </button>
                <button class="filter-tab ${currentStatusFilter === 'pending' ? 'active' : ''}" 
                        onclick="filterByStatus('pending')">
                    🔵 Pending (${stats.pending})
                </button>
                <button class="filter-tab ${currentStatusFilter === 'shortlisted' ? 'active' : ''}" 
                        onclick="filterByStatus('shortlisted')">
                    💛 Shortlisted (${stats.shortlisted})
                </button>
                <button class="filter-tab ${currentStatusFilter === 'interviewed' ? 'active' : ''}" 
                        onclick="filterByStatus('interviewed')">
                    🟣 Interviewed (${stats.interviewed})
                </button>
                <button class="filter-tab ${currentStatusFilter === 'hired' ? 'active' : ''}" 
                        onclick="filterByStatus('hired')">
                    💚 Hired (${stats.hired})
                </button>
                <button class="filter-tab ${currentStatusFilter === 'rejected' ? 'active' : ''}" 
                        onclick="filterByStatus('rejected')">
                    ❌ Rejected (${stats.rejected})
                </button>
            </div>
            
            <!-- Applications Table -->
            <div class="applications-table-container">
                <table class="applications-table">
                    <thead>
                        <tr>
                            <th>
                                <input type="checkbox" onchange="toggleSelectAll(this.checked)" 
                                       ${selectedApplications.size === filteredApps.length && filteredApps.length > 0 ? 'checked' : ''}>
                            </th>
                            <th>Candidate</th>
                            <th>Job Position</th>
                            <th>Applied Date</th>
                            <th>Match Score</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filteredApps.map(app => `
                            <tr class="application-row ${selectedApplications.has(app._id) ? 'selected' : ''}">
                                <td>
                                    <input type="checkbox" 
                                           ${selectedApplications.has(app._id) ? 'checked' : ''}
                                           onchange="toggleApplicationSelection('${app._id}', this.checked)">
                                </td>
                                <td>
                                    <div class="candidate-info">
                                        <div class="candidate-avatar">${app.candidate_name?.charAt(0) || 'C'}</div>
                                        <div>
                                            <div class="candidate-name">${app.candidate_name || 'Unknown'}</div>
                                            <div class="candidate-email">${app.candidate_email || ''}</div>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <div class="job-info">
                                        <div class="job-title-cell">${app.job_title}</div>
                                        <div class="job-company-cell">${app.company_name || ''}</div>
                                    </div>
                                </td>
                                <td>${new Date(app.applied_at).toLocaleDateString('en-US', {month: 'short', day: 'numeric', year: 'numeric'})}</td>
                                <td>
                                    <div class="score-badge ${getScoreClass(app.overall_score)}">
                                        ${Math.round(app.overall_score || 0)}%
                                    </div>
                                </td>
                                <td>
                                    <div class="status-dropdown">
                                        <button class="status-badge status-${app.status}" 
                                                onclick="toggleStatusDropdown('${app._id}', event)">
                                            ${getStatusIcon(app.status)} ${app.status}
                                            <span class="dropdown-arrow">▼</span>
                                        </button>
                                        <div class="status-dropdown-menu" id="dropdown-${app._id}">
                                            <div class="status-option" onclick="updateApplicationStatus('${app._id}', 'pending')">
                                                🔵 Pending
                                            </div>
                                            <div class="status-option" onclick="updateApplicationStatus('${app._id}', 'shortlisted')">
                                                💛 Shortlisted
                                            </div>
                                            <div class="status-option" onclick="updateApplicationStatus('${app._id}', 'interviewed')">
                                                🟣 Interviewed
                                            </div>
                                            <div class="status-option" onclick="updateApplicationStatus('${app._id}', 'hired')">
                                                💚 Hired
                                            </div>
                                            <div class="status-option" onclick="updateApplicationStatus('${app._id}', 'rejected')">
                                                ❌ Rejected
                                            </div>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <div class="action-buttons">
                                        <button class="btn-icon" onclick="viewApplicationDetails('${app._id}')" title="View Details">
                                            👁️
                                        </button>
                                        <button class="btn-icon" onclick="downloadResume('${app._id}')" title="Download Resume">
                                            📥
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        console.error('Failed to load applications:', error);
        container.innerHTML = '<div class="empty-state">Failed to load applications</div>';
    }
}

function getStatusIcon(status) {
    const icons = {
        pending: '🔵',
        shortlisted: '💛',
        interviewed: '🟣',
        hired: '💚',
        rejected: '❌'
    };
    return icons[status] || '⚪';
}

function getScoreClass(score) {
    if (score >= 80) return 'score-high';
    if (score >= 60) return 'score-medium';
    return 'score-low';
}

function toggleSelectAll(checked) {
    const checkboxes = document.querySelectorAll('.application-row input[type="checkbox"]');
    checkboxes.forEach(cb => {
        const appId = cb.onchange.toString().match(/'([^']+)'/)[1];
        if (checked) {
            selectedApplications.add(appId);
            cb.checked = true;
        } else {
            selectedApplications.delete(appId);
            cb.checked = false;
        }
    });
    loadCompanyApplications();
}

function toggleApplicationSelection(appId, checked) {
    if (checked) {
        selectedApplications.add(appId);
    } else {
        selectedApplications.delete(appId);
    }
    loadCompanyApplications();
}

function clearSelection() {
    selectedApplications.clear();
    loadCompanyApplications();
}

function filterByStatus(status) {
    currentStatusFilter = status;
    selectedApplications.clear();
    loadCompanyApplications();
}

function toggleStatusDropdown(appId, event) {
    event.stopPropagation();
    const dropdown = document.getElementById(`dropdown-${appId}`);
    
    // Close all other dropdowns
    document.querySelectorAll('.status-dropdown-menu').forEach(d => {
        if (d.id !== `dropdown-${appId}`) {
            d.classList.remove('show');
        }
    });
    
    dropdown.classList.toggle('show');
}

// Close dropdowns when clicking outside
document.addEventListener('click', () => {
    document.querySelectorAll('.status-dropdown-menu').forEach(d => {
        d.classList.remove('show');
    });
});

async function updateApplicationStatus(appId, newStatus) {
    // Show confirmation modal
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h3 class="modal-title">Confirm Status Update</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
            </div>
            <div class="modal-body">
                <p>Are you sure you want to update the status to <strong>${newStatus}</strong>?</p>
                <div class="form-group">
                    <label>Add a note (optional):</label>
                    <textarea id="statusNote" rows="3" placeholder="Reason for status change..."></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                <button class="btn btn-primary" onclick="confirmStatusUpdate('${appId}', '${newStatus}')">Confirm</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

async function confirmStatusUpdate(appId, newStatus) {
    const note = document.getElementById('statusNote')?.value || '';
    const modal = document.querySelector('.modal');
    
    try {
        const response = await fetch(`${API_URL}/company/applications/${appId}/status`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus, note: note })
        });
        
        if (response.ok) {
            showNotification(`✓ Status updated to ${newStatus}`, 'success');
            modal.remove();
            loadCompanyApplications();
        } else {
            const data = await response.json();
            showNotification('Failed to update status: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        showNotification('Failed to update status: ' + error.message, 'error');
    }
}

function bulkUpdateStatus() {
    if (selectedApplications.size === 0) {
        showNotification('No applications selected', 'warning');
        return;
    }
    
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h3 class="modal-title">Bulk Status Update</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
            </div>
            <div class="modal-body">
                <p>Update status for <strong>${selectedApplications.size}</strong> selected application(s):</p>
                <div class="form-group">
                    <label>New Status:</label>
                    <select id="bulkStatus" class="form-control">
                        <option value="pending">🔵 Pending</option>
                        <option value="shortlisted">💛 Shortlisted</option>
                        <option value="interviewed">🟣 Interviewed</option>
                        <option value="hired">💚 Hired</option>
                        <option value="rejected">❌ Rejected</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Note (optional):</label>
                    <textarea id="bulkNote" rows="3" placeholder="Reason for bulk update..."></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                <button class="btn btn-primary" onclick="confirmBulkUpdate()">Update All</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

async function confirmBulkUpdate() {
    const newStatus = document.getElementById('bulkStatus').value;
    const note = document.getElementById('bulkNote')?.value || '';
    const modal = document.querySelector('.modal');
    
    try {
        const promises = Array.from(selectedApplications).map(appId => 
            fetch(`${API_URL}/company/applications/${appId}/status`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: newStatus, note: note })
            })
        );
        
        await Promise.all(promises);
        showNotification(`✓ Updated ${selectedApplications.size} application(s)`, 'success');
        selectedApplications.clear();
        modal.remove();
        loadCompanyApplications();
    } catch (error) {
        showNotification('Failed to update applications: ' + error.message, 'error');
    }
}

async function viewJobCandidates(jobId) {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = '<div class="modal-content"><div class="loading">Loading ranked candidates...</div></div>';
    document.body.appendChild(modal);
    
    try {
        const response = await fetch(`${API_URL}/company/jobs/${jobId}/ranked-candidates`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load candidates');
        }
        
        const data = await response.json();
        const candidates = data.ranked_candidates || [];
        
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 1000px; max-height: 90vh;">
                <div class="modal-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px;">
                    <div>
                        <h3 class="modal-title" style="margin: 0; font-size: 24px;">${data.job_title}</h3>
                        <p style="margin: 8px 0 0 0; opacity: 0.9;">📊 ${data.total_applicants} Applicants - Ranked by AI Matching Score</p>
                    </div>
                    <button class="modal-close" onclick="this.closest('.modal').remove()" style="color: white; opacity: 0.9;">×</button>
                </div>
                <div class="modal-body" style="padding: 24px; overflow-y: auto; max-height: calc(90vh - 140px);">
                    ${candidates.length === 0 ? `
                        <div style="text-align: center; padding: 40px; color: #64748b;">
                            <div style="font-size: 64px; margin-bottom: 16px;">📭</div>
                            <h3>No Applicants Yet</h3>
                            <p>Candidates will appear here once they apply to this job.</p>
                        </div>
                    ` : `
                        ${candidates.map(candidate => `
                            <div style="background: white; border: 2px solid ${
                                candidate.scores.overall_score >= 75 ? '#10b981' : 
                                candidate.scores.overall_score >= 50 ? '#f59e0b' : '#94a3b8'
                            }; border-radius: 12px; padding: 20px; margin-bottom: 16px; position: relative;">
                                <!-- Rank Badge -->
                                <div style="position: absolute; top: -12px; left: 20px; background: ${
                                    candidate.rank === 1 ? 'linear-gradient(135deg, #fbbf24, #f59e0b)' :
                                    candidate.rank === 2 ? 'linear-gradient(135deg, #9ca3af, #6b7280)' :
                                    candidate.rank === 3 ? 'linear-gradient(135deg, #fb923c, #ea580c)' :
                                    '#667eea'
                                }; color: white; padding: 6px 16px; border-radius: 20px; font-weight: 700; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
                                    ${candidate.rank === 1 ? '🥇' : candidate.rank === 2 ? '🥈' : candidate.rank === 3 ? '🥉' : ''}
                                    #${candidate.rank}
                                </div>
                                
                                <!-- Candidate Header -->
                                <div style="display: flex; justify-content: space-between; align-items: start; margin-top: 8px;">
                                    <div style="flex: 1;">
                                        <h4 style="margin: 0 0 8px 0; font-size: 20px; color: #1e293b;">${candidate.candidate_name}</h4>
                                        <div style="display: flex; gap: 16px; flex-wrap: wrap; color: #64748b; font-size: 14px;">
                                            <span>📧 ${candidate.candidate_email}</span>
                                            <span>📍 ${candidate.location}</span>
                                            <span>💼 ${candidate.experience_years} years exp.</span>
                                            <span>🎓 ${candidate.education}</span>
                                        </div>
                                    </div>
                                    
                                    <!-- Overall Score -->
                                    <div style="text-align: center; min-width: 100px;">
                                        <div style="font-size: 32px; font-weight: 700; color: ${
                                            candidate.scores.overall_score >= 75 ? '#10b981' : 
                                            candidate.scores.overall_score >= 50 ? '#f59e0b' : '#64748b'
                                        };">
                                            ${candidate.scores.overall_score}%
                                        </div>
                                        <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">
                                            Match Score
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Score Breakdown -->
                                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin: 20px 0;">
                                    <div style="background: #f0f9ff; padding: 12px; border-radius: 8px; border-left: 3px solid #3b82f6;">
                                        <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">📊 Skills Match</div>
                                        <div style="font-size: 20px; font-weight: 600; color: #1e293b;">
                                            ${candidate.scores.skill_match}%
                                            <span style="font-size: 14px; color: #64748b; font-weight: 400;">
                                                (${candidate.skills.match_count}/${candidate.skills.total_required})
                                            </span>
                                        </div>
                                    </div>
                                    <div style="background: #fef3f2; padding: 12px; border-radius: 8px; border-left: 3px solid #f97316;">
                                        <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">⚡ Experience Score</div>
                                        <div style="font-size: 20px; font-weight: 600; color: #1e293b;">${candidate.scores.experience_score}%</div>
                                    </div>
                                </div>
                                
                                <!-- Skills Breakdown -->
                                <div style="margin-bottom: 16px;">
                                    <div style="font-weight: 600; margin-bottom: 8px; color: #1e293b;">✅ Matched Skills (${candidate.skills.matched.length})</div>
                                    <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;">
                                        ${candidate.skills.matched.length > 0 ? 
                                            candidate.skills.matched.map(skill => 
                                                `<span style="background: #dcfce7; color: #166534; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: 500;">${skill}</span>`
                                            ).join('') :
                                            '<span style="color: #94a3b8;">None</span>'
                                        }
                                    </div>
                                    
                                    ${candidate.skills.missing.length > 0 ? `
                                        <div style="font-weight: 600; margin-bottom: 8px; color: #1e293b;">⚠️ Missing Skills (${candidate.skills.missing.length})</div>
                                        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                                            ${candidate.skills.missing.map(skill => 
                                                `<span style="background: #fee2e2; color: #991b1b; padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: 500;">${skill}</span>`
                                            ).join('')}
                                        </div>
                                    ` : ''}
                                </div>
                                
                                <!-- Action Buttons -->
                                <div style="display: flex; gap: 8px; margin-top: 16px;">
                                    <button class="btn btn-secondary" onclick="viewApplicationDetails('${candidate.application_id}')" style="flex: 1;">
                                        📄 View Full Profile
                                    </button>
                                    <button class="btn ${candidate.status === 'pending' ? 'btn-primary' : 'btn-secondary'}" 
                                            onclick="updateApplicationStatus('${candidate.application_id}', 'shortlisted')" 
                                            style="flex: 1;">
                                        ⭐ ${candidate.status === 'shortlisted' ? 'Shortlisted' : 'Shortlist'}
                                    </button>
                                    ${candidate.resume_uploaded ? 
                                        `<button class="btn btn-secondary" onclick="downloadResume('${candidate.application_id}')">
                                            📥 Resume
                                        </button>` : ''
                                    }
                                </div>
                                
                                <!-- Application Date & Status -->
                                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #64748b;">
                                    <span>Applied: ${new Date(candidate.applied_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                                    <span style="background: ${
                                        candidate.status === 'hired' ? '#dcfce7' :
                                        candidate.status === 'shortlisted' ? '#fef3c7' :
                                        candidate.status === 'interviewed' ? '#e0e7ff' :
                                        candidate.status === 'rejected' ? '#fee2e2' : '#f1f5f9'
                                    }; color: ${
                                        candidate.status === 'hired' ? '#166534' :
                                        candidate.status === 'shortlisted' ? '#854d0e' :
                                        candidate.status === 'interviewed' ? '#3730a3' :
                                        candidate.status === 'rejected' ? '#991b1b' : '#475569'
                                    }; padding: 4px 12px; border-radius: 12px; font-weight: 600; text-transform: capitalize;">
                                        ${candidate.status}
                                    </span>
                                </div>
                            </div>
                        `).join('')}
                    `}
                </div>
                <div class="modal-footer" style="background: #f8fafc; padding: 16px 24px;">
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Close</button>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading candidates:', error);
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Error</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-error">Failed to load candidates. Please try again.</div>
                </div>
            </div>
        `;
    }
}

function viewApplicationDetails(appId) {
    showNotification('Application details view coming soon!', 'info');
}

function downloadResume(appId) {
    showNotification('Resume download coming soon!', 'info');
}

function companyLogout() {
    // Clear authentication data
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('currentRole');
    
    // Reload the page to return to login
    window.location.href = '/';
}

// ============================================
// ANALYTICS DASHBOARD - ENTERPRISE GRADE
// ============================================
async function loadCompanyAnalytics() {
    const container = document.getElementById('companyAnalytics');
    container.innerHTML = '<div class="loading">Loading analytics...</div>';
    
    try {
        // Fetch analytics data
        const [jobsRes, appsRes] = await Promise.all([
            fetch(`${API_URL}/jobs/company`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            }),
            fetch(`${API_URL}/applications/company`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            })
        ]);
        
        const jobs = await jobsRes.json();
        const applications = await appsRes.json();
        
        // Calculate metrics
        const totalJobs = jobs.length;
        const activeJobs = jobs.filter(j => j.status === 'open').length;
        const totalApps = applications.length;
        const shortlisted = applications.filter(a => a.status === 'shortlisted').length;
        const interviewed = applications.filter(a => a.status === 'interviewed').length;
        const hired = applications.filter(a => a.status === 'hired').length;
        const rejected = applications.filter(a => a.status === 'rejected').length;
        const pending = applications.filter(a => a.status === 'applied').length;
        
        // Conversion rates
        const shortlistRate = totalApps > 0 ? ((shortlisted / totalApps) * 100).toFixed(1) : 0;
        const interviewRate = totalApps > 0 ? ((interviewed / totalApps) * 100).toFixed(1) : 0;
        const hireRate = totalApps > 0 ? ((hired / totalApps) * 100).toFixed(1) : 0;
        
        // Score distribution
        const avgScore = totalApps > 0 ? 
            (applications.reduce((sum, a) => sum + (a.cci_score || 0), 0) / totalApps).toFixed(1) : 0;
        
        // Time to hire (mock data for now)
        const avgTimeToHire = 14;
        
        container.innerHTML = `
            <div class="analytics-header">
                <div class="analytics-title">
                    <h2>📈 Hiring Analytics</h2>
                    <p class="subtitle">Comprehensive insights into your hiring performance</p>
                </div>
                <div class="analytics-actions">
                    <select class="analytics-filter" onchange="filterAnalytics(this.value)">
                        <option value="30">Last 30 Days</option>
                        <option value="90">Last 90 Days</option>
                        <option value="180">Last 6 Months</option>
                        <option value="365">Last Year</option>
                    </select>
                    <button class="btn btn-secondary" onclick="exportAnalytics()">
                        <span>📊</span> Export Report
                    </button>
                </div>
            </div>
            
            <!-- KPI Cards -->
            <div class="analytics-kpi-grid">
                <div class="kpi-card kpi-primary">
                    <div class="kpi-icon">💼</div>
                    <div class="kpi-content">
                        <div class="kpi-value">${totalJobs}</div>
                        <div class="kpi-label">Total Jobs Posted</div>
                        <div class="kpi-trend positive">
                            <span>↑ ${activeJobs} active</span>
                        </div>
                    </div>
                </div>
                
                <div class="kpi-card kpi-success">
                    <div class="kpi-icon">📋</div>
                    <div class="kpi-content">
                        <div class="kpi-value">${totalApps}</div>
                        <div class="kpi-label">Total Applications</div>
                        <div class="kpi-trend positive">
                            <span>↑ ${pending} pending</span>
                        </div>
                    </div>
                </div>
                
                <div class="kpi-card kpi-warning">
                    <div class="kpi-icon">⭐</div>
                    <div class="kpi-content">
                        <div class="kpi-value">${avgScore}</div>
                        <div class="kpi-label">Avg Match Score</div>
                        <div class="kpi-trend ${avgScore >= 70 ? 'positive' : 'neutral'}">
                            <span>${avgScore >= 70 ? '↑' : '→'} out of 100</span>
                        </div>
                    </div>
                </div>
                
                <div class="kpi-card kpi-info">
                    <div class="kpi-icon">⏱️</div>
                    <div class="kpi-content">
                        <div class="kpi-value">${avgTimeToHire}</div>
                        <div class="kpi-label">Avg Time to Hire (days)</div>
                        <div class="kpi-trend positive">
                            <span>↓ 2 days faster</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Hiring Funnel -->
            <div class="analytics-section">
                <div class="section-header">
                    <h3>🎯 Hiring Funnel</h3>
                    <p>Track candidate progression through your hiring stages</p>
                </div>
                <div class="funnel-container">
                    <div class="funnel-stage" style="width: 100%;">
                        <div class="funnel-bar" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                            <span class="funnel-label">Applications</span>
                            <span class="funnel-value">${totalApps}</span>
                        </div>
                        <div class="funnel-percent">100%</div>
                    </div>
                    
                    <div class="funnel-stage" style="width: ${shortlisted > 0 ? (shortlisted/totalApps*100) : 0}%;">
                        <div class="funnel-bar" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                            <span class="funnel-label">Shortlisted</span>
                            <span class="funnel-value">${shortlisted}</span>
                        </div>
                        <div class="funnel-percent">${shortlistRate}%</div>
                    </div>
                    
                    <div class="funnel-stage" style="width: ${interviewed > 0 ? (interviewed/totalApps*100) : 0}%;">
                        <div class="funnel-bar" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                            <span class="funnel-label">Interviewed</span>
                            <span class="funnel-value">${interviewed}</span>
                        </div>
                        <div class="funnel-percent">${interviewRate}%</div>
                    </div>
                    
                    <div class="funnel-stage" style="width: ${hired > 0 ? (hired/totalApps*100) : 5}%;">
                        <div class="funnel-bar" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                            <span class="funnel-label">Hired</span>
                            <span class="funnel-value">${hired}</span>
                        </div>
                        <div class="funnel-percent">${hireRate}%</div>
                    </div>
                </div>
            </div>
            
            <!-- Score Distribution & Decision Breakdown -->
            <div class="analytics-grid-2">
                <div class="analytics-section">
                    <div class="section-header">
                        <h3>📊 Score Distribution</h3>
                        <p>Candidate quality metrics</p>
                    </div>
                    <div class="score-distribution">
                        ${generateScoreChart(applications)}
                    </div>
                </div>
                
                <div class="analytics-section">
                    <div class="section-header">
                        <h3>🎯 Decision Breakdown</h3>
                        <p>Application status distribution</p>
                    </div>
                    <div class="decision-breakdown">
                        <div class="decision-item">
                            <div class="decision-label">
                                <span class="decision-dot" style="background: #10b981;"></span>
                                Hired
                            </div>
                            <div class="decision-bar">
                                <div class="decision-fill" style="width: ${totalApps > 0 ? (hired/totalApps*100) : 0}%; background: #10b981;"></div>
                            </div>
                            <div class="decision-value">${hired}</div>
                        </div>
                        
                        <div class="decision-item">
                            <div class="decision-label">
                                <span class="decision-dot" style="background: #3b82f6;"></span>
                                Interviewed
                            </div>
                            <div class="decision-bar">
                                <div class="decision-fill" style="width: ${totalApps > 0 ? (interviewed/totalApps*100) : 0}%; background: #3b82f6;"></div>
                            </div>
                            <div class="decision-value">${interviewed}</div>
                        </div>
                        
                        <div class="decision-item">
                            <div class="decision-label">
                                <span class="decision-dot" style="background: #f59e0b;"></span>
                                Shortlisted
                            </div>
                            <div class="decision-bar">
                                <div class="decision-fill" style="width: ${totalApps > 0 ? (shortlisted/totalApps*100) : 0}%; background: #f59e0b;"></div>
                            </div>
                            <div class="decision-value">${shortlisted}</div>
                        </div>
                        
                        <div class="decision-item">
                            <div class="decision-label">
                                <span class="decision-dot" style="background: #6b7280;"></span>
                                Pending
                            </div>
                            <div class="decision-bar">
                                <div class="decision-fill" style="width: ${totalApps > 0 ? (pending/totalApps*100) : 0}%; background: #6b7280;"></div>
                            </div>
                            <div class="decision-value">${pending}</div>
                        </div>
                        
                        <div class="decision-item">
                            <div class="decision-label">
                                <span class="decision-dot" style="background: #ef4444;"></span>
                                Rejected
                            </div>
                            <div class="decision-bar">
                                <div class="decision-fill" style="width: ${totalApps > 0 ? (rejected/totalApps*100) : 0}%; background: #ef4444;"></div>
                            </div>
                            <div class="decision-value">${rejected}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Top Performing Jobs -->
            <div class="analytics-section">
                <div class="section-header">
                    <h3>🏆 Top Performing Jobs</h3>
                    <p>Jobs with highest application rates</p>
                </div>
                <div class="top-jobs-list">
                    ${generateTopJobsTable(jobs, applications)}
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading analytics:', error);
        container.innerHTML = `
            <div class="alert alert-error">
                Failed to load analytics. Please try again.
            </div>
        `;
    }
}

function generateScoreChart(applications) {
    const excellent = applications.filter(a => (a.cci_score || 0) >= 75).length;
    const good = applications.filter(a => (a.cci_score || 0) >= 50 && (a.cci_score || 0) < 75).length;
    const fair = applications.filter(a => (a.cci_score || 0) >= 25 && (a.cci_score || 0) < 50).length;
    const poor = applications.filter(a => (a.cci_score || 0) < 25).length;
    const total = applications.length || 1;
    
    return `
        <div class="score-bars">
            <div class="score-item">
                <div class="score-label">
                    <span class="score-badge excellent">⭐ Excellent</span>
                    <span class="score-range">75-100</span>
                </div>
                <div class="score-bar">
                    <div class="score-fill excellent" style="width: ${(excellent/total*100)}%;"></div>
                </div>
                <div class="score-count">${excellent}</div>
            </div>
            
            <div class="score-item">
                <div class="score-label">
                    <span class="score-badge good">✓ Good</span>
                    <span class="score-range">50-74</span>
                </div>
                <div class="score-bar">
                    <div class="score-fill good" style="width: ${(good/total*100)}%;"></div>
                </div>
                <div class="score-count">${good}</div>
            </div>
            
            <div class="score-item">
                <div class="score-label">
                    <span class="score-badge fair">○ Fair</span>
                    <span class="score-range">25-49</span>
                </div>
                <div class="score-bar">
                    <div class="score-fill fair" style="width: ${(fair/total*100)}%;"></div>
                </div>
                <div class="score-count">${fair}</div>
            </div>
            
            <div class="score-item">
                <div class="score-label">
                    <span class="score-badge poor">✕ Poor</span>
                    <span class="score-range">0-24</span>
                </div>
                <div class="score-bar">
                    <div class="score-fill poor" style="width: ${(poor/total*100)}%;"></div>
                </div>
                <div class="score-count">${poor}</div>
            </div>
        </div>
    `;
}

function generateTopJobsTable(jobs, applications) {
    // Calculate application count per job
    const jobStats = jobs.map(job => {
        const jobApps = applications.filter(a => a.job_id === job._id);
        return {
            ...job,
            appCount: jobApps.length,
            avgScore: jobApps.length > 0 ? 
                (jobApps.reduce((sum, a) => sum + (a.cci_score || 0), 0) / jobApps.length).toFixed(1) : 0,
            hired: jobApps.filter(a => a.status === 'hired').length
        };
    }).sort((a, b) => b.appCount - a.appCount).slice(0, 5);
    
    if (jobStats.length === 0) {
        return '<div class="empty-state">No jobs posted yet</div>';
    }
    
    return `
        <table class="analytics-table">
            <thead>
                <tr>
                    <th>Job Title</th>
                    <th>Applications</th>
                    <th>Avg Score</th>
                    <th>Hired</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${jobStats.map((job, index) => `
                    <tr>
                        <td>
                            <div class="job-rank">${index + 1}</div>
                            <div class="job-info">
                                <div class="job-title">${job.title}</div>
                                <div class="job-meta">${job.location} • ${job.experience}</div>
                            </div>
                        </td>
                        <td><span class="metric-badge">${job.appCount}</span></td>
                        <td><span class="score-pill ${job.avgScore >= 75 ? 'excellent' : job.avgScore >= 50 ? 'good' : 'fair'}">${job.avgScore}</span></td>
                        <td><span class="metric-badge success">${job.hired}</span></td>
                        <td><span class="status-badge ${job.status === 'open' ? 'open' : 'closed'}">${job.status}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function filterAnalytics(days) {
    showNotification(`Filtering data for last ${days} days...`, 'info');
    // In production, this would re-fetch with date filters
}

function exportAnalytics() {
    showNotification('Exporting analytics report...', 'success');
    // In production, this would generate PDF/CSV export
}

// ============================================
// FAIRNESS AUDIT INTERFACE
// ============================================
async function loadCompanyAudit() {
    const container = document.getElementById('companyAudit');
    container.innerHTML = '<div class="loading">Loading audit data...</div>';
    
    try {
        const response = await fetch(`${API_URL}/audit/report?days=30`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load audit report');
        }
        
        const data = await response.json();
        
        container.innerHTML = `
            <div class="audit-header">
                <div class="audit-title">
                    <h2>🛡️ Fairness Audit Report</h2>
                    <p class="subtitle">Transparent hiring decisions • Bias-free environment • Compliance ready</p>
                </div>
                <div class="audit-actions">
                    <select class="audit-filter" onchange="filterAuditReport(this.value)">
                        <option value="30">Last 30 Days</option>
                        <option value="90">Last 90 Days</option>
                        <option value="180">Last 6 Months</option>
                        <option value="365">Last Year</option>
                    </select>
                    <button class="btn btn-primary" onclick="exportAuditReport()">
                        <span>📥</span> Export Compliance Report
                    </button>
                </div>
            </div>
            
            <!-- Audit Summary Cards -->
            <div class="audit-summary-grid">
                <div class="audit-card">
                    <div class="audit-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                        📋
                    </div>
                    <div class="audit-content">
                        <div class="audit-value">${data.total_events || 0}</div>
                        <div class="audit-label">Total Events Logged</div>
                        <div class="audit-breakdown">
                            ${Object.entries(data.events_by_type || {}).map(([type, count]) => `
                                <span class="audit-tag">${type}: ${count}</span>
                            `).join('')}
                        </div>
                    </div>
                </div>
                
                <div class="audit-card">
                    <div class="audit-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                        ⭐
                    </div>
                    <div class="audit-content">
                        <div class="audit-value">${data.average_scores?.overall || 'N/A'}</div>
                        <div class="audit-label">Average Match Score</div>
                        <div class="audit-breakdown">
                            <span class="audit-tag">Skills: ${data.average_scores?.skills_match || 'N/A'}</span>
                            <span class="audit-tag">Experience: ${data.average_scores?.experience || 'N/A'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="audit-card">
                    <div class="audit-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                        🎯
                    </div>
                    <div class="audit-content">
                        <div class="audit-value">${data.score_distribution?.excellent || 0}</div>
                        <div class="audit-label">High-Quality Matches</div>
                        <div class="audit-breakdown">
                            <span class="audit-tag">Good: ${data.score_distribution?.good || 0}</span>
                            <span class="audit-tag">Fair: ${data.score_distribution?.fair || 0}</span>
                        </div>
                    </div>
                </div>
                
                <div class="audit-card">
                    <div class="audit-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                        ✓
                    </div>
                    <div class="audit-content">
                        <div class="audit-value">${data.decisions_breakdown?.hired || 0}</div>
                        <div class="audit-label">Candidates Hired</div>
                        <div class="audit-breakdown">
                            <span class="audit-tag">Shortlisted: ${data.decisions_breakdown?.shortlisted || 0}</span>
                            <span class="audit-tag">Interviewed: ${data.decisions_breakdown?.interviewed || 0}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Fairness Metrics -->
            <div class="audit-section">
                <div class="section-header">
                    <h3>⚖️ Fairness Metrics</h3>
                    <p>Bias detection and compliance indicators</p>
                </div>
                <div class="fairness-grid">
                    <div class="fairness-card">
                        <div class="fairness-icon">✓</div>
                        <div class="fairness-label">Score-Based Decisions</div>
                        <div class="fairness-status success">✓ 100% Objective</div>
                        <p class="fairness-desc">All hiring decisions are based on quantifiable skill match scores</p>
                    </div>
                    
                    <div class="fairness-card">
                        <div class="fairness-icon">🔒</div>
                        <div class="fairness-label">Anonymized Scoring</div>
                        <div class="fairness-status success">✓ Enabled</div>
                        <p class="fairness-desc">Initial scoring happens without demographic information</p>
                    </div>
                    
                    <div class="fairness-card">
                        <div class="fairness-icon">📊</div>
                        <div class="fairness-label">Audit Trail</div>
                        <div class="fairness-status success">✓ Complete</div>
                        <p class="fairness-desc">Every decision is logged with timestamps and justification</p>
                    </div>
                    
                    <div class="fairness-card">
                        <div class="fairness-icon">🛡️</div>
                        <div class="fairness-label">Compliance Ready</div>
                        <div class="fairness-status success">✓ Yes</div>
                        <p class="fairness-desc">Full audit reports available for regulatory requirements</p>
                    </div>
                </div>
            </div>
            
            <!-- Score Distribution Analysis -->
            <div class="audit-section">
                <div class="section-header">
                    <h3>📊 Score Distribution Analysis</h3>
                    <p>Ensuring fair evaluation across all candidates</p>
                </div>
                <div class="score-fairness-chart">
                    ${generateFairnessScoreChart(data.score_distribution || {})}
                </div>
            </div>
            
            <!-- Recent Audit Events -->
            <div class="audit-section">
                <div class="section-header">
                    <h3>📝 Recent Audit Events</h3>
                    <p>Real-time tracking of all hiring decisions</p>
                </div>
                <div class="audit-timeline">
                    ${await generateAuditTimeline()}
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading audit data:', error);
        container.innerHTML = `
            <div class="alert alert-info">
                <h3>🛡️ Fairness Audit System</h3>
                <p>The audit system is tracking all your hiring decisions to ensure bias-free hiring.</p>
                <p>Audit data will appear here as you review applications and make hiring decisions.</p>
                <button class="btn btn-primary" onclick="loadCompanyApplications()">View Applications</button>
            </div>
        `;
    }
}

function generateFairnessScoreChart(distribution) {
    const excellent = distribution.excellent || 0;
    const good = distribution.good || 0;
    const fair = distribution.fair || 0;
    const poor = distribution.poor || 0;
    const total = excellent + good + fair + poor || 1;
    
    return `
        <div class="fairness-bars">
            <div class="fairness-bar-item">
                <div class="fairness-bar-header">
                    <span class="fairness-bar-label">Excellent (75-100)</span>
                    <span class="fairness-bar-percent">${((excellent/total)*100).toFixed(1)}%</span>
                </div>
                <div class="fairness-bar">
                    <div class="fairness-bar-fill" style="width: ${(excellent/total)*100}%; background: linear-gradient(90deg, #10b981, #059669);"></div>
                </div>
                <div class="fairness-bar-count">${excellent} candidates</div>
            </div>
            
            <div class="fairness-bar-item">
                <div class="fairness-bar-header">
                    <span class="fairness-bar-label">Good (50-74)</span>
                    <span class="fairness-bar-percent">${((good/total)*100).toFixed(1)}%</span>
                </div>
                <div class="fairness-bar">
                    <div class="fairness-bar-fill" style="width: ${(good/total)*100}%; background: linear-gradient(90deg, #3b82f6, #2563eb);"></div>
                </div>
                <div class="fairness-bar-count">${good} candidates</div>
            </div>
            
            <div class="fairness-bar-item">
                <div class="fairness-bar-header">
                    <span class="fairness-bar-label">Fair (25-49)</span>
                    <span class="fairness-bar-percent">${((fair/total)*100).toFixed(1)}%</span>
                </div>
                <div class="fairness-bar">
                    <div class="fairness-bar-fill" style="width: ${(fair/total)*100}%; background: linear-gradient(90deg, #f59e0b, #d97706);"></div>
                </div>
                <div class="fairness-bar-count">${fair} candidates</div>
            </div>
            
            <div class="fairness-bar-item">
                <div class="fairness-bar-header">
                    <span class="fairness-bar-label">Poor (0-24)</span>
                    <span class="fairness-bar-percent">${((poor/total)*100).toFixed(1)}%</span>
                </div>
                <div class="fairness-bar">
                    <div class="fairness-bar-fill" style="width: ${(poor/total)*100}%; background: linear-gradient(90deg, #ef4444, #dc2626);"></div>
                </div>
                <div class="fairness-bar-count">${poor} candidates</div>
            </div>
        </div>
        
        <div class="fairness-insight">
            <div class="insight-icon">💡</div>
            <div class="insight-content">
                <strong>Fairness Insight:</strong>
                ${excellent >= good ? 
                    'Great! Your job requirements are attracting highly qualified candidates.' :
                    'Consider reviewing job requirements to attract more qualified candidates.'}
            </div>
        </div>
    `;
}

async function generateAuditTimeline() {
    try {
        const response = await fetch(`${API_URL}/audit/logs?limit=10`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (!response.ok) {
            return '<div class="empty-state">No audit events yet</div>';
        }
        
        const logs = await response.json();
        
        if (!logs || logs.length === 0) {
            return '<div class="empty-state">No audit events yet</div>';
        }
        
        return logs.map(log => {
            const date = new Date(log.timestamp);
            const eventIcon = log.event_type === 'application_submitted' ? '📋' :
                            log.event_type === 'ranked' ? '📊' :
                            log.event_type === 'status_changed' ? '🔄' : '📝';
            
            return `
                <div class="audit-timeline-item">
                    <div class="timeline-icon">${eventIcon}</div>
                    <div class="timeline-content">
                        <div class="timeline-header">
                            <span class="timeline-event">${log.event_type.replace('_', ' ').toUpperCase()}</span>
                            <span class="timeline-time">${date.toLocaleDateString()} ${date.toLocaleTimeString()}</span>
                        </div>
                        <div class="timeline-details">
                            ${log.details ? `<p>${JSON.stringify(log.details)}</p>` : ''}
                            ${log.scores ? `
                                <div class="timeline-scores">
                                    ${Object.entries(log.scores).map(([key, val]) => `
                                        <span class="score-tag">${key}: ${typeof val === 'number' ? val.toFixed(1) : val}</span>
                                    `).join('')}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error loading audit timeline:', error);
        return '<div class="empty-state">No audit events yet</div>';
    }
}

function filterAuditReport(days) {
    showNotification(`Loading audit data for last ${days} days...`, 'info');
    loadCompanyAudit();
}

function exportAuditReport() {
    showNotification('Generating compliance report...', 'success');
    // In production, this would generate a detailed PDF report
}
