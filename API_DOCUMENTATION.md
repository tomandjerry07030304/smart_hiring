# Smart Hiring System - API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <access_token>
```

---

## 1. Authentication Endpoints

### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "candidate",  // or "recruiter"
  "phone": "+1234567890",
  "linkedin_url": "https://linkedin.com/in/johndoe"
}

Response: 201 Created
{
  "message": "User registered successfully",
  "user_id": "abc123",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "candidate"
  }
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response: 200 OK
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": "abc123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "candidate"
  }
}
```

### Get Profile
```http
GET /api/auth/profile
Authorization: Bearer <token>

Response: 200 OK
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "candidate",
  "profile_completed": true
}
```

---

## 2. Job Endpoints

### Create Job (Recruiter only)
```http
POST /api/jobs/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Senior Python Developer",
  "description": "Looking for experienced Python developer...",
  "company_name": "Tech Corp",
  "location": "Remote",
  "job_type": "Full-time",
  "required_skills": ["python", "django", "rest api"],
  "experience_required": 3,
  "salary_range": {
    "min": 80000,
    "max": 120000,
    "currency": "USD"
  }
}

Response: 201 Created
{
  "message": "Job created successfully",
  "job_id": "job123",
  "required_skills": ["python", "django", "rest api"]
}
```

### List Jobs
```http
GET /api/jobs/list?status=open&limit=50&skip=0

Response: 200 OK
{
  "jobs": [...],
  "count": 10,
  "total": 50
}
```

### Get Job Details
```http
GET /api/jobs/{job_id}

Response: 200 OK
{
  "_id": "job123",
  "title": "Senior Python Developer",
  "description": "...",
  "required_skills": ["python", "django"]
}
```

---

## 3. Candidate Endpoints

### Upload Resume
```http
POST /api/candidates/upload-resume
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
- resume: <file> (PDF, DOCX, TXT)
- experience: <JSON string> (optional)

Example experience JSON:
[
  {
    "company": "Tech Corp",
    "title": "Software Engineer",
    "start_date": "2020-01-01",
    "end_date": "2022-12-31"
  }
]

Response: 200 OK
{
  "message": "Resume uploaded successfully",
  "skills_found": ["python", "sql", "react"],
  "skills_count": 15,
  "cci": {
    "cci_score": 75.5,
    "interpretation": "Good - Stable with consistent growth"
  }
}
```

### Apply to Job
```http
POST /api/candidates/apply/{job_id}
Authorization: Bearer <token>

Response: 201 Created
{
  "message": "Application submitted successfully",
  "application_id": "app123",
  "score": 78.5,
  "decision": "Review",
  "matched_skills": ["python", "django"],
  "recommendations": [
    "Improve skills in: kubernetes, docker"
  ]
}
```

### Get My Applications
```http
GET /api/candidates/applications
Authorization: Bearer <token>

Response: 200 OK
{
  "applications": [
    {
      "_id": "app123",
      "job_id": "job123",
      "job_title": "Senior Python Developer",
      "overall_score": 78.5,
      "decision": "Review",
      "status": "submitted"
    }
  ],
  "count": 5
}
```

---

## 4. Assessment Endpoints

### Create Assessment (Recruiter only)
```http
POST /api/assessments/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "job_id": "job123",
  "title": "Python Technical Assessment",
  "assessment_type": "mcq",
  "duration_minutes": 45,
  "passing_score": 70,
  "questions": [
    {
      "question": "What is a decorator in Python?",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A"
    }
  ]
}

Response: 201 Created
{
  "message": "Assessment created successfully",
  "assessment_id": "assess123"
}
```

### Submit Assessment
```http
POST /api/assessments/{assessment_id}/submit
Authorization: Bearer <token>
Content-Type: application/json

{
  "application_id": "app123",
  "answers": ["A", "B", "C"],
  "started_at": "2025-01-01T10:00:00Z",
  "time_taken_minutes": 30
}

Response: 201 Created
{
  "message": "Assessment submitted successfully",
  "score": 2,
  "percentage": 66.67,
  "passed": false
}
```

### Schedule Interview (Recruiter only)
```http
POST /api/assessments/schedule-interview
Authorization: Bearer <token>
Content-Type: application/json

{
  "application_id": "app123",
  "job_id": "job123",
  "candidate_id": "cand123",
  "interview_type": "technical",
  "scheduled_time": "2025-01-15T14:00:00Z",
  "duration_minutes": 60,
  "meeting_link": "https://meet.google.com/xyz"
}

Response: 201 Created
{
  "message": "Interview scheduled successfully",
  "interview_id": "int123"
}
```

---

## 5. Dashboard & Analytics

### Get Analytics (Recruiter only)
```http
GET /api/dashboard/analytics
Authorization: Bearer <token>

Response: 200 OK
{
  "summary": {
    "total_jobs": 10,
    "total_applications": 150,
    "avg_score": 65.3,
    "applications_last_30_days": 45
  },
  "applications_by_status": {
    "submitted": 80,
    "screening": 40,
    "shortlisted": 20,
    "rejected": 10
  },
  "top_skills": [
    {"skill": "python", "count": 25},
    {"skill": "javascript", "count": 20}
  ]
}
```

### Get Fairness Audit (Recruiter only)
```http
GET /api/dashboard/fairness/{job_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "job_id": "job123",
  "total_applications": 100,
  "fairness_score": 85,
  "fairness_badge": {
    "badge": "Good Fairness",
    "color": "lightgreen",
    "level": "A"
  },
  "overall_bias_detected": false,
  "analyses": {
    "gender": {
      "demographic_parity_difference": 0.05,
      "bias_detected": false
    }
  },
  "summary_recommendations": [
    "Continue monitoring hiring outcomes for fairness"
  ]
}
```

### Get Transparency Report
```http
GET /api/dashboard/transparency/{application_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "application_id": "app123",
  "job_title": "Senior Python Developer",
  "decision": "Review",
  "scoring_breakdown": {
    "resume_match": 0.65,
    "skill_match": 0.70,
    "cci_score": 75.5,
    "overall_score": 78.5
  },
  "matched_skills": ["python", "django"],
  "missing_skills": ["kubernetes", "docker"],
  "decision_rationale": "Moderate match with score of 78.5%...",
  "improvement_suggestions": [
    "Develop skills in: kubernetes, docker"
  ]
}
```

---

## Error Responses

All endpoints may return these error codes:

### 400 Bad Request
```json
{
  "error": "Missing required field: email"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
  "error": "Only recruiters can create job postings"
}
```

### 404 Not Found
```json
{
  "error": "Job not found"
}
```

### 409 Conflict
```json
{
  "error": "Email already registered"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Testing with curl

### Example: Register and Login
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User",
    "role": "candidate"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Use token in subsequent requests
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```
