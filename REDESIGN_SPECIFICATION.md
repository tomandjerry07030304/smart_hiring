# Smart Hiring System - Complete Redesign Specification

## 🎯 System Overview

**Platform Role**: You are a **mediator recruitment platform** between companies and candidates.

### Your Value Proposition:
- Assess candidate capabilities through tests/assessments
- Match qualified candidates to company requirements
- Provide fair, AI-powered recruitment process
- Manage the entire hiring workflow

---

## 👥 Three Distinct User Roles

### 1. **Platform Admin** (You - The Mediator)
**Access**: Full platform control
**Capabilities**:
- Oversee all companies and candidates
- View platform analytics and metrics
- Manage assessment tests and questions
- Configure system settings
- Monitor recruitment processes
- Handle disputes/issues

### 2. **Company/Recruiter**
**Access**: Company-specific portal
**Capabilities**:
- Post job openings with requirements
- View candidate pool (after assessment)
- Review matched candidates with scores
- Schedule interviews
- Manage applications
- Track hiring pipeline
- Pay for platform services

### 3. **Candidate/Job Seeker**
**Access**: Candidate portal
**Capabilities**:
- Create profile with resume
- Browse available jobs
- Apply to positions
- **Take mandatory assessments** before being visible to companies
- View application status
- Track interview schedules
- Receive notifications

---

## 🔐 Authentication System

### Role Selection Page (Landing)
```
┌─────────────────────────────────────┐
│    Smart Hiring System Logo         │
│  AI-Powered Fair Recruitment        │
│                                     │
│  [👨‍💼 Platform Admin]               │
│  [🏢 Company/Recruiter]             │
│  [👨‍💻 Job Seeker]                   │
└─────────────────────────────────────┘
```

### Login Pages (Separate for each role)
- **Admin Login**: admin@smarthiring.com / changeme
- **Company Login**: Register → Verify → Login
- **Candidate Login**: Register → Complete Profile → Login

### Registration Flow

#### Company Registration:
1. Company details (name, industry, size)
2. Recruiter contact information
3. Email verification
4. Account approval by admin

#### Candidate Registration:
1. Personal information
2. Upload resume
3. Skills and experience
4. **Mandatory**: Take initial assessment
5. Profile activation

---

## 📊 Dashboard Designs

### Admin Dashboard
```
┌─────────────────────────────────────┐
│ 📊 Platform Statistics              │
│  - Total Companies: 25               │
│  - Total Candidates: 150             │
│  - Active Jobs: 42                   │
│  - Assessments Taken: 320            │
│                                     │
│ 🏢 Company Management                │
│  - Pending Approvals                 │
│  - Active Companies                  │
│                                     │
│ 👥 Candidate Oversight               │
│  - New Registrations                 │
│  - Assessment Results                │
│                                     │
│ 📝 Assessment Management             │
│  - Create Tests                      │
│  - Question Bank                     │
│  - Test Analytics                    │
└─────────────────────────────────────┘
```

### Company Dashboard
```
┌─────────────────────────────────────┐
│ 💼 My Job Posts (12)                │
│  [+ Post New Job]                    │
│                                     │
│ 🎯 Matched Candidates                │
│  - Senior Developer (8 matches)      │
│  - Data Analyst (5 matches)          │
│                                     │
│ 📋 Applications (25)                 │
│  - Under Review: 10                  │
│  - Interview Scheduled: 8            │
│  - Offers Made: 7                    │
│                                     │
│ 📅 Interview Schedule                │
└─────────────────────────────────────┘
```

### Candidate Dashboard
```
┌─────────────────────────────────────┐
│ 👨‍💻 My Profile                        │
│  [Edit Profile] [Upload Resume]      │
│                                     │
│ 🔍 Browse Jobs (45 available)        │
│  [Filter: Industry, Location, Type]  │
│                                     │
│ 📝 My Assessments                    │
│  - Completed: 3                      │
│  - Pending: 1                        │
│  - Scores: View Details              │
│                                     │
│ 📋 My Applications (5)               │
│  - Applied: 3                        │
│  - Interview Scheduled: 1            │
│  - Offer Received: 1                 │
│                                     │
│ 🎯 Recommended Jobs                  │
└─────────────────────────────────────┘
```

---

## 🧪 Assessment System (Core Feature)

### Test Types:
1. **Technical Skills** (Coding, Tools)
2. **Aptitude Tests** (Logic, Reasoning)
3. **Domain Knowledge** (Industry-specific)
4. **Soft Skills** (Communication, Problem-solving)

### Assessment Flow:
```
Candidate Registers
    ↓
Upload Resume & Profile
    ↓
[MANDATORY] Take Initial Assessment
    ↓
Score Calculated (AI-assisted)
    ↓
Profile Becomes Visible to Companies
    ↓
Company Posts Job
    ↓
AI Matches Candidates (using assessment scores)
    ↓
Company Reviews Matched Candidates
    ↓
Company Schedules Interview
    ↓
Hiring Decision
```

### Test Interface Features:
- Multiple choice questions
- Coding challenges (for tech roles)
- Timed tests
- Auto-scoring
- Detailed result analytics
- Certificates of completion

---

## 🚀 Key Features to Implement

### 1. **Responsive Buttons** (Currently Broken)
All buttons must have working event listeners:
- `Apply Now` → Submit application
- `View Details` → Show job description
- `Take Test` → Launch assessment
- `Upload Resume` → File upload dialog
- `Post Job` → Open job form
- `Schedule Interview` → Calendar picker

### 2. **Interactive Job Cards**
```javascript
<div class="job-card" onclick="viewJobDetails(jobId)">
  <h3>Senior Software Engineer</h3>
  <p>Company: Tech Corp</p>
  <button onclick="applyToJob(jobId); event.stopPropagation()">
    Apply Now
  </button>
</div>
```

### 3. **Real-time Notifications**
- Application status updates
- Interview invitations
- Assessment assignments
- New job matches

### 4. **Application Workflow**
```
Candidate sees job → Click Apply Now → 
Check if assessment completed →
If NO: Redirect to assessment →
If YES: Show application form →
Submit application → Notify company →
Company reviews → Schedule interview →
Candidate notified
```

---

## 📋 Database Schema Updates Needed

### Users Collection:
```javascript
{
  _id: ObjectId,
  email: String,
  password: String (hashed),
  role: "admin" | "company" | "candidate",
  first_name: String,
  last_name: String,
  phone: String,
  company_name: String (for companies),
  created_at: Date,
  is_approved: Boolean (for companies),
  profile_complete: Boolean (for candidates)
}
```

### Assessments Collection (NEW):
```javascript
{
  _id: ObjectId,
  title: String,
  description: String,
  test_type: "technical" | "aptitude" | "domain" | "soft_skills",
  questions: [
    {
      question: String,
      options: [String],
      correct_answer: String,
      points: Number
    }
  ],
  time_limit_minutes: Number,
  passing_score: Number,
  created_by: ObjectId (admin),
  created_at: Date
}
```

### Test Results Collection (NEW):
```javascript
{
  _id: ObjectId,
  candidate_id: ObjectId,
  assessment_id: ObjectId,
  score: Number,
  total_possible: Number,
  percentage: Number,
  time_taken_minutes: Number,
  passed: Boolean,
  answers: [{question_id, selected_answer}],
  completed_at: Date
}
```

---

## 🎨 UI/UX Improvements

### Current Issues:
❌ Single dashboard for all users  
❌ Buttons don't respond to clicks  
❌ No role-based access control  
❌ Missing assessment system  
❌ No company-candidate separation  

### Required Fixes:
✅ Separate pages for each role  
✅ Working event handlers on all buttons  
✅ Role-based routing and authentication  
✅ Complete assessment module  
✅ Clear company/candidate workflows  

---

## 📝 Implementation Priority

### Phase 1: Authentication (URGENT)
- [ ] Role selection page
- [ ] Separate login for each role
- [ ] Registration with role-specific fields
- [ ] JWT token with role information
- [ ] Protected routes based on role

### Phase 2: Dashboards
- [ ] Admin dashboard with platform metrics
- [ ] Company dashboard with job management
- [ ] Candidate dashboard with job search

### Phase 3: Assessment System (CORE)
- [ ] Admin creates tests
- [ ] Candidate takes tests
- [ ] Auto-scoring system
- [ ] Results display

### Phase 4: Job-Candidate Matching
- [ ] Company posts jobs
- [ ] AI matches based on assessment scores
- [ ] Application workflow
- [ ] Interview scheduling

### Phase 5: Polish
- [ ] Fix all button interactions
- [ ] Add notifications
- [ ] Mobile responsive
- [ ] Email alerts

---

## 🛠️ Technical Stack

**Frontend**: Pure HTML, CSS, JavaScript (current)
**Backend**: Flask Python API
**Database**: MongoDB
**Authentication**: JWT tokens with roles
**AI/ML**: scikit-learn for matching

---

**Next Steps**: Would you like me to implement this complete redesign? I'll build it systematically starting with authentication and role-based dashboards.
