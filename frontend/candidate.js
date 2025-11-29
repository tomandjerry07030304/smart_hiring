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
                <button class="nav-link active" onclick="switchCandidateTab('browse', event)">🔍 Browse Jobs</button>
                <button class="nav-link" onclick="switchCandidateTab('applications', event)">📋 My Applications</button>
                <button class="nav-link" onclick="switchCandidateTab('assessments', event)">📝 Assessments</button>
                <button class="nav-link" onclick="switchCandidateTab('profile', event)">👤 Profile</button>
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

function switchCandidateTab(tab, event) {
    // Remove active state from all nav links and content
    document.querySelectorAll('#candidateDashboard .nav-link').forEach(l => l.classList.remove('active'));
    document.querySelectorAll('#candidateDashboard .tab-content').forEach(t => {
        t.classList.remove('active');
        t.style.display = 'none';
    });
    
    // Add active state to clicked nav link
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    // Show the selected tab content
    const tabContent = document.getElementById(`candidate${tab.charAt(0).toUpperCase() + tab.slice(1)}`);
    if (tabContent) {
        tabContent.classList.add('active');
        tabContent.style.display = 'block';
    }
    
    // Load content based on tab with smooth transition
    switch(tab) {
        case 'browse': loadCandidateBrowse(); break;
        case 'applications': loadCandidateApplications(); break;
        case 'assessments': loadCandidateAssessments(); break;
        case 'profile': loadCandidateProfile(); break;
    }
    
    // Scroll to top smoothly
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
        const response = await fetch(`${API_URL}/candidates/apply/${jobId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        // Check content type before parsing as JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Server response:', text.substring(0, 200));
            throw new Error('Server returned invalid response. Please contact support.');
        }
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✓ Application submitted successfully! Track it in "My Applications".');
            // Refresh the applications list
            setTimeout(() => {
                loadCandidateApplications();
            }, 1000);
        } else {
            throw new Error(data.message || data.error || 'Failed to apply');
        }
    } catch (error) {
        console.error('Application error:', error);
        alert('Failed to submit application: ' + error.message);
    }
}

async function loadCandidateApplications() {
    const container = document.getElementById('candidateApplications');
    container.innerHTML = '<div class="loading">Loading applications...</div>';
    
    try {
        const response = await fetch(`${API_URL}/candidates/applications`, {
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
    container.innerHTML = '<div class="loading">Loading assessments...</div>';
    
    try {
        const response = await fetch(`${API_URL}/assessments/quizzes`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load assessments');
        }
        
        const data = await response.json();
        const quizzes = data.quizzes || [];
        
        // Get quiz attempts to show completed quizzes
        const attemptsResponse = await fetch(`${API_URL}/assessments/my-attempts`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const attemptsData = attemptsResponse.ok ? await attemptsResponse.json() : { attempts: [] };
        const attempts = attemptsData.attempts || [];
        
        // Calculate stats
        const completedCount = attempts.filter(a => a.status === 'completed').length;
        const avgScore = completedCount > 0 ? 
            Math.round(attempts.filter(a => a.status === 'completed').reduce((sum, a) => sum + (a.score || 0), 0) / completedCount) : 
            0;
        
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
                            <div class="stat-value">${completedCount}</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">📊</div>
                        <div class="stat-content">
                            <div class="stat-label">Average Score</div>
                            <div class="stat-value">${completedCount > 0 ? avgScore + '%' : '-'}</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">📝</div>
                        <div class="stat-content">
                            <div class="stat-label">Available</div>
                            <div class="stat-value">${quizzes.length}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            ${quizzes.length > 0 ? `
                <div class="card">
                    <h3>📋 Available Assessments</h3>
                    <div class="jobs-grid">
                        ${quizzes.map(quiz => {
                            const attempt = attempts.find(a => a.quiz_id === quiz._id);
                            const isCompleted = attempt && attempt.status === 'completed';
                            const score = isCompleted ? attempt.score : null;
                            
                            return `
                                <div class="job-card">
                                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                                        <h3 style="margin: 0;">${quiz.title}</h3>
                                        ${isCompleted ? `<span class="tag" style="background: #10b981; color: white;">✓ Completed</span>` : 
                                                       `<span class="tag" style="background: #3b82f6; color: white;">Available</span>`}
                                    </div>
                                    <p style="color: #64748b; margin-bottom: 16px;">${quiz.description || 'Test your skills'}</p>
                                    <div style="display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap;">
                                        <span>⏱️ ${quiz.duration_minutes} minutes</span>
                                        <span>❓ ${quiz.questions?.length || 0} questions</span>
                                        <span>🎯 ${quiz.passing_score || 70}% to pass</span>
                                    </div>
                                    ${isCompleted ? `
                                        <div class="alert ${score >= (quiz.passing_score || 70) ? 'alert-success' : 'alert-warning'}" style="margin-bottom: 16px;">
                                            ${score >= (quiz.passing_score || 70) ? '✓' : '⚠️'} Your Score: ${score}% 
                                            ${score >= (quiz.passing_score || 70) ? '(Passed)' : '(Did not pass)'}
                                        </div>
                                    ` : ''}
                                    <button class="btn ${isCompleted ? 'btn-secondary' : 'btn-primary'}" 
                                            onclick="${isCompleted ? `viewQuizResults('${quiz._id}')` : `startQuiz('${quiz._id}')`}">
                                        ${isCompleted ? '📊 View Results' : '▶️ Start Assessment'}
                                    </button>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            ` : `
                <div class="card">
                    <div class="empty-state">
                        <div style="font-size: 64px; margin-bottom: 16px;">📝</div>
                        <h3>No Assessments Available Yet</h3>
                        <p>Assessments become available when you apply to jobs that require skill testing.</p>
                        <p style="color: #64748b;">Apply to jobs with assessment requirements to see them here!</p>
                    </div>
                </div>
            `}
        `;
    } catch (error) {
        console.error('Failed to load assessments:', error);
        container.innerHTML = `
            <div class="content-header">
                <h2>📝 Skill Assessments</h2>
            </div>
            <div class="card">
                <div class="alert alert-error">
                    Failed to load assessments. Please try again later.
                </div>
            </div>
        `;
    }
}

async function startQuiz(quizId) {
    if (!confirm('Are you ready to start this assessment? The timer will begin immediately.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/assessments/quizzes/${quizId}/start`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to start quiz');
        }
        
        const data = await response.json();
        showNotification('✓ Assessment started! Good luck!', 'success');
        // Reload to show quiz interface
        loadCandidateAssessments();
    } catch (error) {
        console.error('Start quiz error:', error);
        showNotification('Failed to start assessment: ' + error.message, 'error');
    }
}

async function viewQuizResults(quizId) {
    showNotification('Quiz results viewing coming soon!', 'info');
}

async function loadCandidateProfile() {
    const container = document.getElementById('candidateProfile');
    container.innerHTML = '<div class="loading">Loading profile...</div>';
    
    try {
        const response = await fetch(`${API_URL}/candidates/profile`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (!response.ok) {
            throw new Error('Profile not found');
        }
        
        const profile = await response.json();
        
        // Safely get profile data with proper defaults
        const firstName = profile.first_name || currentUser.full_name?.split(' ')[0] || 'User';
        const lastName = profile.last_name || currentUser.full_name?.split(' ').slice(1).join(' ') || '';
        const email = profile.email || currentUser.email || 'Not provided';
        const phone = profile.phone || 'Not provided';
        const skills = profile.skills || [];
        const experience = profile.experience_years || profile.experience || 0;
        const education = profile.education || 'Not provided';
        const bio = profile.bio || '';
        const location = profile.location || '';
        const linkedin = profile.linkedin || '';
        const portfolio = profile.portfolio || '';
        const resumeUploaded = profile.resume_uploaded || profile.resume_file || false;
        
        container.innerHTML = `
            <div class="content-header">
                <h2>👤 My Profile</h2>
                <button class="btn btn-primary" onclick="editProfile()">✏️ Edit Profile</button>
            </div>
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 24px;">
                    <div>
                        <h3>${firstName} ${lastName}</h3>
                        <p>📧 ${email}</p>
                        <p>📞 ${phone}</p>
                        ${location ? `<p>📍 ${location}</p>` : ''}
                    </div>
                    <div style="text-align: right;">
                        ${linkedin ? `<a href="${linkedin}" target="_blank" class="btn btn-secondary" style="margin-bottom: 8px; display: inline-block;">🔗 LinkedIn</a><br>` : ''}
                        ${portfolio ? `<a href="${portfolio}" target="_blank" class="btn btn-secondary" style="display: inline-block;">🌐 Portfolio</a>` : ''}
                    </div>
                </div>
                
                ${bio ? `
                    <h4>About Me</h4>
                    <p style="color: #4a5568; line-height: 1.6; margin-bottom: 24px;">${bio}</p>
                ` : ''}
                
                <h4>Skills</h4>
                <div class="job-tags" style="margin-bottom: 24px;">
                    ${skills.length > 0 ? 
                        skills.map(s => `<span class="tag">${s}</span>`).join('') :
                        '<p class="text-muted">No skills added</p>'
                    }
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px; margin-bottom: 24px;">
                    <div>
                        <h4>Experience</h4>
                        <p>${experience} years</p>
                    </div>
                    <div>
                        <h4>Education</h4>
                        <p>${education}</p>
                    </div>
                </div>
                
                <h4>Resume</h4>
                ${resumeUploaded ? 
                    `<div class="alert alert-success">✓ Resume uploaded successfully</div>
                     <button class="btn btn-secondary" onclick="uploadResume()">📤 Upload New Resume</button>` :
                    `<div class="alert alert-warning">⚠️ No resume uploaded. Upload your resume to apply to jobs.</div>
                     <button class="btn btn-primary" onclick="uploadResume()">📤 Upload Resume</button>`
                }
            </div>
        `;
    } catch (error) {
        console.error('Profile load error:', error);
        // Create default profile view with current user data
        const firstName = currentUser.full_name?.split(' ')[0] || 'User';
        const lastName = currentUser.full_name?.split(' ').slice(1).join(' ') || '';
        
        container.innerHTML = `
            <div class="content-header">
                <h2>👤 My Profile</h2>
            </div>
            <div class="card">
                <h3>${firstName} ${lastName}</h3>
                <p>📧 ${currentUser.email || 'undefined'}</p>
                <p>📞 Not provided</p>
                
                <h4>Skills</h4>
                <p class="text-muted">No skills added</p>
                
                <h4>Experience</h4>
                <p>0 years</p>
                
                <h4>Education</h4>
                <p>Not provided</p>
                
                <h4>Resume</h4>
                <div class="alert alert-warning">⚠️ Complete your profile to improve your job matches!</div>
                <button class="btn btn-primary" onclick="uploadResume()">📤 Upload Resume</button>
            </div>
        `;
    }
}

function editProfile() {
    // Get current profile data
    const nameElement = document.querySelector('.card h3');
    const currentName = nameElement ? nameElement.textContent : '';
    const firstName = currentName.split(' ')[0] || '';
    const lastName = currentName.split(' ').slice(1).join(' ') || '';
    
    const emailElement = document.querySelector('.card p');
    const currentEmail = emailElement ? emailElement.textContent.replace('📧 ', '') : currentUser.email;
    
    const phoneElement = document.querySelectorAll('.card p')[1];
    const currentPhone = phoneElement ? phoneElement.textContent.replace('📞 ', '').replace('Not provided', '') : '';
    
    const skillsElements = document.querySelectorAll('.tag');
    const currentSkills = Array.from(skillsElements).map(el => el.textContent).join(', ');
    
    const expElement = Array.from(document.querySelectorAll('.card p')).find(p => p.previousElementSibling?.textContent === 'Experience');
    const currentExperience = expElement ? expElement.textContent.replace(' years', '') : '0';
    
    const eduElement = Array.from(document.querySelectorAll('.card p')).find(p => p.previousElementSibling?.textContent === 'Education');
    const currentEducation = eduElement ? eduElement.textContent : '';
    
    // Create edit profile modal
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">✏️ Edit Profile</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
            </div>
            <form id="editProfileForm" onsubmit="submitProfileEdit(event)">
                <div class="modal-body">
                    <div class="form-row">
                        <div class="form-group">
                            <label>First Name *</label>
                            <input type="text" name="firstName" value="${firstName}" required>
                        </div>
                        <div class="form-group">
                            <label>Last Name *</label>
                            <input type="text" name="lastName" value="${lastName}" required>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Email *</label>
                        <input type="email" name="email" value="${currentEmail}" required disabled>
                        <small style="color: #718096;">Email cannot be changed</small>
                    </div>
                    
                    <div class="form-group">
                        <label>Phone Number</label>
                        <div style="display: flex; gap: 8px;">
                            <select name="country_code" style="width: 140px;">
                                <option value="+1">🇺🇸 +1 (US)</option>
                                <option value="+44">🇬🇧 +44 (UK)</option>
                                <option value="+91">🇮🇳 +91 (India)</option>
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
                            <input type="tel" name="phone" value="${currentPhone}" placeholder="1234567890" style="flex: 1;">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Skills (comma-separated)</label>
                        <input type="text" name="skills" value="${currentSkills}" 
                               placeholder="JavaScript, Python, React, Node.js">
                        <small style="color: #718096;">Separate skills with commas</small>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Years of Experience</label>
                            <input type="number" name="experience" value="${currentExperience}" 
                                   min="0" max="50" step="0.5">
                        </div>
                        <div class="form-group">
                            <label>Current Location</label>
                            <input type="text" name="location" placeholder="San Francisco, CA">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Education</label>
                        <textarea name="education" rows="3" placeholder="Bachelor's in Computer Science, Stanford University">${currentEducation}</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>About / Bio</label>
                        <textarea name="bio" rows="4" placeholder="Tell us about yourself, your experience, and career goals..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>LinkedIn Profile URL</label>
                        <input type="url" name="linkedin" placeholder="https://linkedin.com/in/yourprofile">
                    </div>
                    
                    <div class="form-group">
                        <label>Portfolio Website</label>
                        <input type="url" name="portfolio" placeholder="https://yourportfolio.com">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                    <button type="submit" class="btn btn-primary">
                        💾 Save Profile
                    </button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
}

async function submitProfileEdit(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner show"></span> Saving...';
    
    try {
        const formData = new FormData(form);
        const skills = formData.get('skills') 
            ? formData.get('skills').split(',').map(s => s.trim()).filter(s => s)
            : [];
        
        const profileData = {
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            country_code: formData.get('country_code'),
            phone: formData.get('phone'),
            skills: skills,
            experience: parseFloat(formData.get('experience')) || 0,
            education: formData.get('education'),
            bio: formData.get('bio'),
            location: formData.get('location'),
            linkedin: formData.get('linkedin'),
            portfolio: formData.get('portfolio')
        };
        
        const response = await fetch(`${API_URL}/candidates/profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(profileData)
        });
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            
            if (response.ok) {
                showNotification('✓ Profile updated successfully!', 'success');
                form.closest('.modal').remove();
                loadCandidateProfile(); // Reload profile to show updates
            } else {
                throw new Error(data.error || 'Failed to update profile');
            }
        } else {
            throw new Error('Server returned non-JSON response');
        }
    } catch (error) {
        console.error('Profile update error:', error);
        showNotification('Failed to update profile: ' + error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

function uploadResume() {
    // Create modern upload modal
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content upload-modal">
            <div class="modal-header">
                <h3 class="modal-title">📤 Upload Resume</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
            </div>
            <div class="modal-body">
                <div class="upload-zone" id="uploadZone" ondrop="handleDrop(event)" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)">
                    <div class="upload-icon">📄</div>
                    <h4>Drag & Drop your resume here</h4>
                    <p>or click to browse</p>
                    <input type="file" id="resumeFile" accept=".pdf,.doc,.docx" style="display: none" onchange="handleFileSelect(event)">
                    <button class="btn btn-primary" onclick="document.getElementById('resumeFile').click()">
                        Choose File
                    </button>
                    <p class="file-info">Supported formats: PDF, DOC, DOCX (Max 5MB)</p>
                </div>
                <div class="file-preview" id="filePreview" style="display: none;">
                    <div class="preview-header">
                        <div class="file-icon">📄</div>
                        <div class="file-details">
                            <div class="file-name" id="fileName"></div>
                            <div class="file-size" id="fileSize"></div>
                        </div>
                        <button class="btn-remove" onclick="clearFile()">🗑️</button>
                    </div>
                    <div class="upload-progress" id="uploadProgress" style="display: none;">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill"></div>
                        </div>
                        <div class="progress-text" id="progressText">0%</div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                <button class="btn btn-success" id="uploadBtn" onclick="submitResume()" disabled>
                    <span>Upload Resume</span>
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    // Make upload zone clickable
    document.getElementById('uploadZone').onclick = (e) => {
        if (e.target.id === 'uploadZone' || e.target.closest('.upload-icon') || e.target.tagName === 'H4' || e.target.tagName === 'P') {
            document.getElementById('resumeFile').click();
        }
    };
}

let selectedFile = null;

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        validateAndPreviewFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        validateAndPreviewFile(files[0]);
    }
}

function validateAndPreviewFile(file) {
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Please upload a PDF, DOC, or DOCX file', 'error');
        return;
    }
    
    // Validate file size (5MB max)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
        showNotification('File size must be less than 5MB', 'error');
        return;
    }
    
    // Store file and show preview
    selectedFile = file;
    document.getElementById('uploadZone').style.display = 'none';
    document.getElementById('filePreview').style.display = 'block';
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    document.getElementById('uploadBtn').disabled = false;
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function clearFile() {
    selectedFile = null;
    document.getElementById('uploadZone').style.display = 'block';
    document.getElementById('filePreview').style.display = 'none';
    document.getElementById('resumeFile').value = '';
    document.getElementById('uploadBtn').disabled = true;
}

async function submitResume() {
    if (!selectedFile) {
        showNotification('Please select a file first', 'error');
        return;
    }
    
    const uploadBtn = document.getElementById('uploadBtn');
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="spinner show"></span> Uploading...';
    
    // Show progress bar
    document.getElementById('uploadProgress').style.display = 'block';
    
    try {
        const formData = new FormData();
        formData.append('resume', selectedFile);
        
        // Simulate upload progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 10;
            if (progress <= 90) {
                document.getElementById('progressFill').style.width = progress + '%';
                document.getElementById('progressText').textContent = progress + '%';
            }
        }, 100);
        
        const response = await fetch(`${API_URL}/candidates/upload-resume`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        clearInterval(progressInterval);
        document.getElementById('progressFill').style.width = '100%';
        document.getElementById('progressText').textContent = '100%';
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.skills_count > 0) {
                showNotification(`✓ Resume uploaded successfully! Found ${data.skills_count} skills: ${data.skills_found.slice(0, 5).join(', ')}${data.skills_count > 5 ? '...' : ''}`, 'success');
            } else {
                showNotification('✓ Resume uploaded successfully! No technical skills detected. Please add skills manually in your profile.', 'warning');
            }
            
            // Close modal after short delay
            setTimeout(() => {
                const modal = document.querySelector('.modal');
                if (modal) modal.remove();
                // Refresh profile to show updated resume and skills
                loadCandidateProfile();
            }, 2000);
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to upload resume');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showNotification('Failed to upload resume: ' + error.message, 'error');
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = '<span>Upload Resume</span>';
        document.getElementById('uploadProgress').style.display = 'none';
    }
}

function candidateLogout() {
    // Clear authentication data
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('currentRole');
    
    // Reload the page to return to login
    window.location.href = '/';
}
