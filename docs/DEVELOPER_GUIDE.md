# Developer Guide - Smart Hiring System

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Architecture](#project-architecture)
3. [Backend Development](#backend-development)
4. [Frontend Development](#frontend-development)
5. [Database Schema](#database-schema)
6. [API Development](#api-development)
7. [Testing](#testing)
8. [Building & Packaging](#building--packaging)
9. [Contributing](#contributing)
10. [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### Prerequisites

- **Python**: 3.11+
- **Node.js**: 18+ with npm
- **MongoDB**: 5.0+ (local or Atlas)
- **Git**: Latest version
- **IDE**: VS Code (recommended) or PyCharm

### Initial Setup

```bash
# Clone repository
git clone https://github.com/your-org/smart-hiring-system.git
cd smart-hiring-system

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Install Node dependencies (for desktop app)
cd desktop
npm install
cd ..

# Copy environment template
cp .env.template .env

# Edit .env with your settings
```

### VS Code Setup

Recommended extensions:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

Settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

---

## Project Architecture

### Directory Structure

```
smart-hiring-system/
├── backend/               # Python Flask backend
│   ├── api/              # API routes
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   ├── utils/            # Utilities
│   ├── tests/            # Backend tests
│   ├── app.py            # Flask application
│   └── main.py           # PyInstaller entry point
├── frontend/             # React frontend (TBD)
│   ├── src/
│   ├── public/
│   └── package.json
├── desktop/              # Electron wrapper
│   ├── main.js           # Electron main process
│   ├── preload.js        # Preload script
│   └── package.json
├── build_scripts/        # Build automation
├── deploy/               # Docker deployment
├── docs/                 # Documentation
├── scripts/              # Utility scripts
└── tests/                # Integration tests
```

### Technology Stack

**Backend**:
- Flask 3.1 - Web framework
- PyMongo - MongoDB driver
- scikit-learn - ML algorithms
- spaCy - NLP processing
- Flask-JWT-Extended - Authentication
- PyInstaller - Executable packaging

**Frontend** (Planned):
- React 18 - UI framework
- Material-UI - Component library
- Axios - HTTP client
- React Router - Navigation

**Desktop**:
- Electron 28 - Desktop wrapper
- electron-builder - Packaging
- electron-updater - Auto-updates

**Database**:
- MongoDB 5.0+ - NoSQL database

---

## Backend Development

### Flask Application Structure

```python
# backend/app.py
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object('config.Config')

CORS(app)
jwt = JWTManager(app)

# Register blueprints
from api import auth_bp, jobs_bp, candidates_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
app.register_blueprint(candidates_bp, url_prefix='/api/candidates')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

### Creating API Endpoints

```python
# backend/api/jobs.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.job import Job

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/', methods=['GET'])
@jwt_required()
def get_jobs():
    """Get all jobs for current user"""
    user_id = get_jwt_identity()
    jobs = Job.find_by_user(user_id)
    return jsonify([job.to_dict() for job in jobs]), 200

@jobs_bp.route('/', methods=['POST'])
@jwt_required()
def create_job():
    """Create new job posting"""
    data = request.get_json()
    
    # Validate input
    if not data.get('title') or not data.get('description'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create job
    job = Job(
        title=data['title'],
        description=data['description'],
        requirements=data.get('requirements', []),
        created_by=get_jwt_identity()
    )
    job.save()
    
    return jsonify(job.to_dict()), 201
```

### Database Models

```python
# backend/models/job.py
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

class Job:
    collection = MongoClient()['smart_hiring']['jobs']
    
    def __init__(self, title, description, requirements=None, **kwargs):
        self.title = title
        self.description = description
        self.requirements = requirements or []
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.created_by = kwargs.get('created_by')
        self._id = kwargs.get('_id')
    
    def save(self):
        """Save job to database"""
        data = {
            'title': self.title,
            'description': self.description,
            'requirements': self.requirements,
            'created_at': self.created_at,
            'created_by': self.created_by
        }
        
        if self._id:
            self.collection.update_one({'_id': self._id}, {'$set': data})
        else:
            result = self.collection.insert_one(data)
            self._id = result.inserted_id
        
        return self
    
    @classmethod
    def find_by_id(cls, job_id):
        """Find job by ID"""
        data = cls.collection.find_one({'_id': ObjectId(job_id)})
        return cls(**data) if data else None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self._id),
            'title': self.title,
            'description': self.description,
            'requirements': self.requirements,
            'created_at': self.created_at.isoformat()
        }
```

### ML/AI Services

```python
# backend/services/matching.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

nlp = spacy.load('en_core_web_sm')

class MatchingService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words='english'
        )
    
    def calculate_match_score(self, job_description, resume_text):
        """
        Calculate similarity between job and resume
        Returns: score (0-100)
        """
        # Vectorize texts
        vectors = self.vectorizer.fit_transform([
            job_description,
            resume_text
        ])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        # Convert to percentage
        score = round(similarity * 100, 2)
        
        return score
    
    def extract_skills(self, text):
        """Extract skills from text using NLP"""
        doc = nlp(text)
        
        skills = []
        for chunk in doc.noun_chunks:
            if self._is_skill(chunk.text):
                skills.append(chunk.text.lower())
        
        return list(set(skills))
    
    def _is_skill(self, text):
        """Determine if text is a skill"""
        skill_keywords = ['python', 'java', 'javascript', 'sql', 
                          'react', 'angular', 'aws', 'docker']
        return any(keyword in text.lower() for keyword in skill_keywords)
```

### Running Backend in Development

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Set development mode
$env:FLASK_ENV="development"

# Run with auto-reload
cd backend
python app.py
```

Backend runs on: http://localhost:8000

---

## Frontend Development

### React Component Structure (Planned)

```javascript
// frontend/src/components/JobList.jsx
import React, { useState, useEffect } from 'react';
import { getJobs } from '../api/jobs';

const JobList = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const data = await getJobs();
      setJobs(data);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="job-list">
      {jobs.map(job => (
        <div key={job.id} className="job-card">
          <h3>{job.title}</h3>
          <p>{job.description}</p>
        </div>
      ))}
    </div>
  );
};

export default JobList;
```

### API Client

```javascript
// frontend/src/api/client.js
import axios from 'axios';

const API_BASE_URL = window.electron 
  ? await window.electron.getBackendUrl()
  : 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
client.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default client;
```

---

## Database Schema

### Collections

#### users
```javascript
{
  _id: ObjectId,
  email: String (unique),
  password: String (hashed),
  name: String,
  role: String, // 'admin', 'recruiter', 'hiring_manager', 'candidate'
  is_active: Boolean,
  created_at: DateTime,
  last_login: DateTime
}
```

#### jobs
```javascript
{
  _id: ObjectId,
  title: String,
  description: String,
  requirements: [String],
  skills_required: [String],
  location: String,
  salary_range: {min: Number, max: Number},
  status: String, // 'draft', 'active', 'closed'
  created_by: ObjectId (ref: users),
  created_at: DateTime,
  updated_at: DateTime
}
```

#### candidates
```javascript
{
  _id: ObjectId,
  job_id: ObjectId (ref: jobs),
  name: String,
  email: String,
  phone: String,
  resume_path: String,
  resume_text: String,
  skills: [String],
  experience_years: Number,
  status: String, // 'applied', 'screening', 'interview', 'rejected', 'hired'
  match_score: Number,
  created_at: DateTime
}
```

### Indexes

```javascript
// Performance indexes
db.users.createIndex({email: 1}, {unique: true})
db.jobs.createIndex({status: 1, created_at: -1})
db.candidates.createIndex({job_id: 1, match_score: -1})
db.audit_logs.createIndex({timestamp: -1})
```

---

## API Development

### API Documentation

See `docs/API_DOCUMENTATION.md` for complete API reference.

### Authentication

All protected endpoints require JWT token:

```bash
# Login to get token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.com","password":"Admin@123!"}'

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}

# Use token in subsequent requests
curl http://localhost:8000/api/jobs \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Error Handling

```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(ValidationError)
def validation_error(error):
    return jsonify({'error': str(error)}), 400
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest backend/tests/test_api.py

# Run specific test
pytest backend/tests/test_api.py::test_health_check
```

### Writing Tests

```python
# backend/tests/test_jobs.py
import pytest
from backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_jobs(client, auth_token):
    """Test getting job list"""
    response = client.get(
        '/api/jobs',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_job(client, auth_token):
    """Test creating new job"""
    response = client.post(
        '/api/jobs',
        json={
            'title': 'Software Engineer',
            'description': 'Python developer needed'
        },
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 201
    assert 'id' in response.json
```

---

## Building & Packaging

### Build Backend Executable

```powershell
cd build_scripts
.\build_backend_exe.ps1
```

Output: `backend/dist/smart_hiring_backend.exe`

### Build Desktop Application

```powershell
.\build_electron_app.ps1
```

Output: `desktop/dist/Smart Hiring System-Setup-1.0.0.exe`

### Docker Build

```bash
docker-compose -f deploy/docker-compose.yml build
```

---

## Contributing

### Code Style

**Python**: Follow PEP 8
```bash
# Format code
black backend/

# Check style
flake8 backend/

# Type checking
mypy backend/
```

**JavaScript**: Follow Airbnb style guide
```bash
# Format code
npm run format

# Lint
npm run lint
```

### Git Workflow

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit: `git commit -m "Add my feature"`
3. Push branch: `git push origin feature/my-feature`
4. Create Pull Request
5. Code review
6. Merge to main

### Commit Messages

Follow Conventional Commits:
```
feat: Add resume anonymization
fix: Fix matching algorithm bug
docs: Update API documentation
test: Add tests for job API
chore: Update dependencies
```

---

## Troubleshooting

### Common Development Issues

**Import errors**:
```bash
# Make sure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r backend/requirements.txt
```

**Database connection issues**:
```bash
# Check MongoDB is running
mongo --eval "db.version()"

# Verify connection string in .env
MONGODB_URI=mongodb://localhost:27017/smart_hiring
```

**Port already in use**:
```bash
# Find process using port
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

---

## Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **MongoDB Documentation**: https://docs.mongodb.com/
- **Electron Documentation**: https://www.electronjs.org/docs
- **React Documentation**: https://react.dev/

---

**Document Version**: 1.0.0  
**Last Updated**: November 14, 2025
