// Candidate Dashboard Module
function loadCandidateDashboard() {
    const dashboard = document.getElementById('candidateDashboard');
    dashboard.innerHTML = `
        <nav class="navbar">
            <div class="navbar-brand">
                <svg width="32" height="32" viewBox="0 0 64 64">
                    <circle cx="32" cy="32" r="30" fill="#4F46E5"/>
                    <path d="M32 16L40 28H24L32 16Z" fill="white"/>
                    <rect x="22" y="30" width="20" height="18" rx="2" fill="white"/>
                </svg>
                <span>Candidate Portal</span>
            </div>
            <div class="navbar-menu">
                <button class="nav-link active" onclick="switchCandidateTab('browse')">🔍 Browse Jobs</button>
                <button class="nav-link" onclick="switchCandidateTab('applications')">📋 My Applications</button>
                <button class="nav-link" onclick="switchCandidateTab('assessments')">📝 Assessments</button>
                <button class="nav-link" onclick="switchCandidateTab('profile')">👤 Profile</button>
            </div>
            <div class="navbar-actions">
                <span class="user-info">${currentUser.email}</span>
                <button class="btn btn-secondary" onclick="candidateLogout()">Logout</button>
            </div>
        </nav>
        <div class="main-content">
            <div id="candidateBrowse" class="tab-content active"></div>
            <div id="candidateApplications" class="tab-content"></div>
            <div id="candidateAssessments" class="tab-content"></div>
            <div id="candidateProfile" class="tab-content"></div>
        </div>
    `;
    showPage('candidateDashboard');
    loadCandidateBrowse();
}

function switchCandidateTab(tab) {
    document.querySelectorAll('#candidateDashboard .nav-link').forEach(l => l.classList.remove('active'));
    document.querySelectorAll('#candidateDashboard .tab-content').forEach(t => t.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(`candidate${tab.charAt(0).toUpperCase() + tab.slice(1)}`).classList.add('active');
    
    switch(tab) {
        case 'browse': loadCandidateBrowse(); break;
        case 'applications': loadCandidateApplications(); break;
        case 'assessments': loadCandidateAssessments(); break;
        case 'profile': loadCandidateProfile(); break;
    }
}

async function loadCandidateBrowse() {
    const container = document.getElementById('candidateBrowse');
    container.innerHTML = '<div class="loading">Loading available jobs...</div>';
    
    try {
        const response = await fetch(`${API_URL}/jobs/list?status=open`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load jobs');
        }
        
        const data = await response.json();
        const jobs = data.jobs || [];
        
        console.log(`Loaded ${jobs.length} jobs for candidates`);
        
        if (jobs.length === 0) {
            container.innerHTML = '<div class="empty-state">No jobs available at the moment. Check back soon!</div>';
            return;
        }
        
        container.innerHTML = `
            <div class="content-header">
                <h2>🔍 Browse Available Jobs</h2>
                <div class="search-bar">
                    <input type="text" id="jobSearch" placeholder="Search by title, skills, location..." onkeyup="filterJobs()">
                </div>
            </div>
            <div class="job-grid" id="jobsGrid">
                ${jobs.map(job => `
                    <div class="job-card" data-title="${job.title.toLowerCase()}" data-skills="${(job.required_skills || []).join(' ').toLowerCase()}" data-location="${(job.location || '').toLowerCase()}">
                        <div class="job-header">
                            <div>
                                <h3 class="job-title">${job.title}</h3>
                                <p class="job-company">${job.company_name || 'Company'}</p>
                            </div>
                            <span class="badge badge-success">Open</span>
                        </div>
                        <p class="job-description" style="white-space: pre-line;">${job.description.substring(0, 200)}...</p>
                        <div class="job-meta">
                            <span>📍 ${job.location || 'Remote'}</span>
                            <span>💼 ${job.job_type || 'Full-time'}</span>
                            <span>📅 Posted ${job.posted_date ? new Date(job.posted_date).toLocaleDateString() : 'Recently'}</span>
                        </div>
                        <div class="job-tags">
                            ${(job.required_skills || []).slice(0, 5).map(s => `<span class="tag">${s}</span>`).join('')}
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <button class="btn btn-secondary" onclick="viewJobDetails('${job._id}')">View Details</button>
                            <button class="btn btn-primary" onclick="applyToJob('${job._id}')">Apply Now</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        console.error('Error loading jobs:', error);
        container.innerHTML = `
            <div class="empty-state">
                <p>❌ Failed to load jobs. Please try again later.</p>
                <button class="btn btn-primary" onclick="loadCandidateBrowse()">Retry</button>
            </div>
        `;
    }
}

function filterJobs() {
    const searchTerm = document.getElementById('jobSearch').value.toLowerCase();
    const cards = document.querySelectorAll('#jobsGrid .job-card');
    
    cards.forEach(card => {
        const title = card.dataset.title || '';
        const skills = card.dataset.skills || '';
        const location = card.dataset.location || '';
        
        if (title.includes(searchTerm) || skills.includes(searchTerm) || location.includes(searchTerm)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}

async function viewJobDetails(jobId) {
    try {
        const response = await fetch(`${API_URL}/jobs/${jobId}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const job = await response.json();
        
        const modal = document.createElement('div');
        modal.className = 'modal show';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title">${job.title}</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <p><strong>📍 Location:</strong> ${job.location}</p>
                    <p><strong>💼 Job Type:</strong> ${job.job_type}</p>
                    <p><strong>🏢 Department:</strong> ${job.department}</p>
                    <h4>Description</h4>
                    <p>${job.description}</p>
                    <h4>Requirements</h4>
                    <ul>
                        ${(job.requirements || []).map(r => `<li>${r}</li>`).join('')}
                    </ul>
                    <h4>Required Skills</h4>
                    <div class="job-tags">
                        ${(job.required_skills || []).map(s => `<span class="tag">${s}</span>`).join('')}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Close</button>
                    <button class="btn btn-primary" onclick="this.closest('.modal').remove(); applyToJob('${job._id}')">Apply Now</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    } catch (error) {
        alert('Failed to load job details');
    }
}

async function applyToJob(jobId) {
    if (!confirm('Apply to this job? Make sure you have completed required assessments and updated your profile.')) return;
    
    try {
        const response = await fetch(`${API_URL}/applications`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ job_id: jobId })
        });
        
        if (response.ok) {
            alert('✓ Application submitted successfully! You can track it in "My Applications".');
        } else {
            const error = await response.json();
            throw new Error(error.message || 'Failed to apply');
        }
    } catch (error) {
        alert('Failed to submit application: ' + error.message);
    }
}

async function loadCandidateApplications() {
    const container = document.getElementById('candidateApplications');
    container.innerHTML = '<div class="loading">Loading applications...</div>';
    
    try {
        const response = await fetch(`${API_URL}/applications/candidate`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        const applications = data.applications || [];
        
        if (applications.length === 0) {
            container.innerHTML = `
                <div class="content-header">
                    <h2>📋 My Applications</h2>
                </div>
                <div class="empty-state">
                    No applications yet. Browse jobs and apply to get started!
                </div>
            `;
            return;
        }
        
        container.innerHTML = `
            <div class="content-header">
                <h2>📋 My Applications</h2>
            </div>
            <div class="job-grid">
                ${applications.map(app => `
                    <div class="job-card">
                        <div class="job-header">
                            <div>
                                <h3 class="job-title">${app.job_title}</h3>
                                <p class="job-company">${app.company_name}</p>
                            </div>
                            <span class="badge badge-${getStatusColor(app.status)}">${app.status}</span>
                        </div>
                        <div class="job-meta">
                            <span>📅 Applied: ${new Date(app.applied_at).toLocaleDateString()}</span>
                            <span>📍 ${app.location}</span>
                        </div>
                        ${app.interview_scheduled ? `
                            <div class="alert alert-info">
                                📅 Interview scheduled: ${new Date(app.interview_date).toLocaleString()}
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        container.innerHTML = '<div class="empty-state">Failed to load applications</div>';
    }
}

function getStatusColor(status) {
    const colors = {
        'pending': 'warning',
        'reviewing': 'info',
        'shortlisted': 'success',
        'interview': 'primary',
        'rejected': 'danger',
        'accepted': 'success'
    };
    return colors[status] || 'secondary';
}

async function loadCandidateAssessments() {
    const container = document.getElementById('candidateAssessments');
    container.innerHTML = `
        <div class="content-header">
            <h2>📝 Skill Assessments</h2>
        </div>
        <div class="card">
            <h3>Why Take Assessments?</h3>
            <p>Complete skill assessments to showcase your capabilities. Higher scores increase your chances of getting matched with relevant job opportunities!</p>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">✅</div>
                    <div class="stat-content">
                        <div class="stat-label">Completed</div>
                        <div class="stat-value">0</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-content">
                        <div class="stat-label">Average Score</div>
                        <div class="stat-value">-</div>
                    </div>
                </div>
            </div>
            <p class="empty-state">No assessments available yet. Check back soon!</p>
        </div>
    `;
}

async function loadCandidateProfile() {
    const container = document.getElementById('candidateProfile');
    container.innerHTML = '<div class="loading">Loading profile...</div>';
    
    try {
        const response = await fetch(`${API_URL}/candidates/profile`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const profile = await response.json();
        
        container.innerHTML = `
            <div class="content-header">
                <h2>👤 My Profile</h2>
                <button class="btn btn-primary" onclick="editProfile()">Edit Profile</button>
            </div>
            <div class="card">
                <h3>${profile.first_name} ${profile.last_name}</h3>
                <p>📧 ${profile.email}</p>
                <p>📞 ${profile.phone || 'Not provided'}</p>
                
                <h4>Skills</h4>
                <div class="job-tags">
                    ${(profile.skills || ['No skills added']).map(s => `<span class="tag">${s}</span>`).join('')}
                </div>
                
                <h4>Experience</h4>
                <p>${profile.experience_years || 0} years</p>
                
                <h4>Education</h4>
                <p>${profile.education || 'Not provided'}</p>
                
                <h4>Resume</h4>
                ${profile.resume_url ? 
                    `<a href="${profile.resume_url}" target="_blank" class="btn btn-secondary">📄 View Resume</a>` :
                    `<button class="btn btn-primary" onclick="uploadResume()">📤 Upload Resume</button>`
                }
            </div>
        `;
    } catch (error) {
        container.innerHTML = `
            <div class="content-header">
                <h2>👤 My Profile</h2>
            </div>
            <div class="card">
                <p>Complete your profile to improve your job matches!</p>
                <button class="btn btn-primary" onclick="editProfile()">Create Profile</button>
            </div>
        `;
    }
}

function editProfile() {
    alert('Profile editing interface coming soon!');
}

function uploadResume() {
    alert('Resume upload interface coming soon!');
}

function candidateLogout() {
    // Clear authentication data
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('currentRole');
    
    // Reload the page to return to login
    window.location.href = '/';
}
