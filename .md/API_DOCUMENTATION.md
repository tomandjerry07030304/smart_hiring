# API Documentation - Smart Hiring System

## Base URL

**Development**: `http://localhost:8000/api`  
**Production**: `https://your-domain.com/api`

## Authentication

Most endpoints require authentication using JWT (JSON Web Token).

### Headers

```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

### Getting a Token

Login to receive an access token:

```http
POST /auth/login
```

---

## Endpoints

### Health Check

Check API health status.

**Endpoint**: `GET /health`  
**Auth**: Not required

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T10:30:00Z",
  "database": "connected",
  "version": "1.0.0"
}
```

---

### Authentication

#### Register User

Create a new user account.

**Endpoint**: `POST /auth/register`  
**Auth**: Not required

**Request Body**:
```json
{
  "email": "user@company.com",
  "password": "SecurePass123!",
  "name": "John Doe",
  "role": "candidate"
}
```

**Response** (201 Created):
```json
{
  "message": "User created successfully",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@company.com",
    "name": "John Doe",
    "role": "candidate"
  }
}
```

#### Login

Authenticate and receive access token.

**Endpoint**: `POST /auth/login`  
**Auth**: Not required

**Request Body**:
```json
{
  "email": "user@company.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@company.com",
    "name": "John Doe",
    "role": "candidate"
  }
}
```

#### Logout

Invalidate current session.

**Endpoint**: `POST /auth/logout`  
**Auth**: Required

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

---

### Jobs

#### List Jobs

Get all job postings (with filtering).

**Endpoint**: `GET /jobs`  
**Auth**: Required

**Query Parameters**:
- `status` (optional): Filter by status (active, closed, draft)
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response** (200 OK):
```json
{
  "jobs": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Senior Python Developer",
      "description": "We are seeking an experienced Python developer...",
      "requirements": [
        "5+ years Python experience",
        "Experience with Flask/Django",
        "Strong SQL skills"
      ],
      "skills_required": ["python", "flask", "postgresql"],
      "location": "Remote",
      "salary_range": {
        "min": 80000,
        "max": 120000,
        "currency": "USD"
      },
      "status": "active",
      "created_at": "2025-11-01T10:00:00Z",
      "updated_at": "2025-11-01T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

#### Get Job by ID

Get details of a specific job.

**Endpoint**: `GET /jobs/:id`  
**Auth**: Required

**Response** (200 OK):
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Senior Python Developer",
  "description": "We are seeking an experienced Python developer...",
  "requirements": ["5+ years Python experience"],
  "skills_required": ["python", "flask", "postgresql"],
  "location": "Remote",
  "salary_range": {
    "min": 80000,
    "max": 120000
  },
  "status": "active",
  "created_at": "2025-11-01T10:00:00Z",
  "candidates_count": 15,
  "applications": []
}
```

#### Create Job

Create a new job posting.

**Endpoint**: `POST /jobs`  
**Auth**: Required (recruiter, admin)

**Request Body**:
```json
{
  "title": "Senior Python Developer",
  "description": "We are seeking an experienced Python developer...",
  "requirements": [
    "5+ years Python experience",
    "Experience with Flask/Django"
  ],
  "skills_required": ["python", "flask", "postgresql"],
  "location": "Remote",
  "salary_range": {
    "min": 80000,
    "max": 120000,
    "currency": "USD"
  },
  "status": "active"
}
```

**Response** (201 Created):
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Senior Python Developer",
  "message": "Job created successfully"
}
```

#### Update Job

Update an existing job.

**Endpoint**: `PUT /jobs/:id`  
**Auth**: Required (recruiter, admin)

**Request Body**: (any fields to update)
```json
{
  "status": "closed"
}
```

**Response** (200 OK):
```json
{
  "message": "Job updated successfully",
  "job": { ... }
}
```

#### Delete Job

Delete a job posting.

**Endpoint**: `DELETE /jobs/:id`  
**Auth**: Required (admin)

**Response** (200 OK):
```json
{
  "message": "Job deleted successfully"
}
```

---

### Candidates

#### List Candidates

Get all candidates for a job.

**Endpoint**: `GET /jobs/:job_id/candidates`  
**Auth**: Required (recruiter, admin)

**Query Parameters**:
- `status` (optional): Filter by status
- `min_score` (optional): Minimum match score (0-100)

**Response** (200 OK):
```json
{
  "candidates": [
    {
      "id": "507f1f77bcf86cd799439012",
      "job_id": "507f1f77bcf86cd799439011",
      "name": "Jane Smith",
      "email": "jane@example.com",
      "phone": "+1234567890",
      "resume_path": "/uploads/resumes/jane_smith_resume.pdf",
      "skills": ["python", "flask", "postgresql", "docker"],
      "experience_years": 6,
      "match_score": 87.5,
      "status": "screening",
      "created_at": "2025-11-02T14:30:00Z"
    }
  ],
  "total": 1
}
```

#### Apply for Job

Submit application for a job.

**Endpoint**: `POST /jobs/:job_id/apply`  
**Auth**: Required (candidate)  
**Content-Type**: `multipart/form-data`

**Form Data**:
- `name`: Candidate name
- `email`: Candidate email
- `phone`: Phone number
- `resume`: Resume file (PDF, DOC, DOCX)

**Response** (201 Created):
```json
{
  "message": "Application submitted successfully",
  "candidate_id": "507f1f77bcf86cd799439012",
  "match_score": 87.5
}
```

#### Update Candidate Status

Update candidate application status.

**Endpoint**: `PATCH /candidates/:id/status`  
**Auth**: Required (recruiter, admin)

**Request Body**:
```json
{
  "status": "interview",
  "notes": "Invited for technical interview"
}
```

**Response** (200 OK):
```json
{
  "message": "Candidate status updated",
  "status": "interview"
}
```

---

### Resume Processing

#### Parse Resume

Extract information from resume.

**Endpoint**: `POST /resumes/parse`  
**Auth**: Required  
**Content-Type**: `multipart/form-data`

**Form Data**:
- `resume`: Resume file (PDF, DOC, DOCX, TXT)

**Response** (200 OK):
```json
{
  "text": "John Doe\nSoftware Engineer...",
  "skills": ["python", "javascript", "react", "sql"],
  "experience_years": 5,
  "education": ["B.S. Computer Science"],
  "email": "john@example.com",
  "phone": "+1234567890"
}
```

#### Anonymize Resume

Remove identifying information from resume.

**Endpoint**: `POST /resumes/anonymize`  
**Auth**: Required  
**Content-Type**: `multipart/form-data`

**Form Data**:
- `resume`: Resume file

**Response** (200 OK):
```json
{
  "anonymized_text": "Software Engineer with 5 years...",
  "download_url": "/downloads/anonymized_resume.pdf"
}
```

---

### Matching

#### Calculate Match Score

Calculate match score between job and candidate.

**Endpoint**: `POST /match`  
**Auth**: Required

**Request Body**:
```json
{
  "job_id": "507f1f77bcf86cd799439011",
  "candidate_id": "507f1f77bcf86cd799439012"
}
```

**Response** (200 OK):
```json
{
  "job_id": "507f1f77bcf86cd799439011",
  "candidate_id": "507f1f77bcf86cd799439012",
  "match_score": 87.5,
  "matching_skills": ["python", "flask", "postgresql"],
  "missing_skills": ["kubernetes"],
  "recommendations": [
    "Strong technical match",
    "Experience level exceeds requirements"
  ]
}
```

#### Get Top Matches

Get top matching candidates for a job.

**Endpoint**: `GET /jobs/:job_id/matches`  
**Auth**: Required (recruiter, admin)

**Query Parameters**:
- `limit` (optional): Number of results (default: 10)
- `min_score` (optional): Minimum score (default: 50)

**Response** (200 OK):
```json
{
  "matches": [
    {
      "candidate_id": "507f1f77bcf86cd799439012",
      "name": "Jane Smith",
      "match_score": 92.3,
      "matching_skills": ["python", "flask", "postgresql", "docker"],
      "experience_years": 6
    }
  ],
  "total": 1
}
```

---

### Dashboard & Analytics

#### Get Dashboard Stats

Get overview statistics.

**Endpoint**: `GET /dashboard/stats`  
**Auth**: Required

**Response** (200 OK):
```json
{
  "jobs": {
    "total": 25,
    "active": 15,
    "closed": 10
  },
  "candidates": {
    "total": 342,
    "pending": 120,
    "in_process": 89,
    "hired": 45,
    "rejected": 88
  },
  "matches": {
    "high_score": 67,
    "medium_score": 178,
    "low_score": 97
  },
  "recent_activity": [
    {
      "type": "application",
      "message": "New application for Senior Python Developer",
      "timestamp": "2025-11-14T09:45:00Z"
    }
  ]
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "details": {}
}
```

### Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate email)
- `422 Unprocessable Entity`: Validation failed
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Error Codes

- `INVALID_CREDENTIALS`: Login failed
- `EMAIL_EXISTS`: Email already registered
- `INVALID_TOKEN`: JWT token invalid or expired
- `PERMISSION_DENIED`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `VALIDATION_ERROR`: Input validation failed
- `FILE_TOO_LARGE`: Uploaded file exceeds size limit
- `UNSUPPORTED_FILE_TYPE`: File type not allowed

---

## Rate Limiting

API requests are rate-limited:

- **Authenticated users**: 1000 requests/hour
- **Anonymous users**: 100 requests/hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1699977600
```

---

## Pagination

List endpoints support pagination:

**Query Parameters**:
- `limit`: Number of results per page (max: 100)
- `offset`: Number of results to skip

**Response Headers**:
```
X-Total-Count: 342
Link: </api/jobs?limit=50&offset=50>; rel="next"
```

---

## Webhooks (Coming Soon)

Subscribe to events:
- `job.created`
- `job.updated`
- `application.received`
- `candidate.status_changed`
- `match.found`

---

**API Version**: v1  
**Last Updated**: November 14, 2025
