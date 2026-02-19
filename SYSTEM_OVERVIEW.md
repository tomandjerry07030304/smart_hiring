# System Overview — Smart Hiring System

A comprehensive technical overview of the Smart Hiring System architecture, components, data flow, and how the different parts of the project interact with each other.

---

## Table of Contents

- [High-Level Architecture](#high-level-architecture)
- [Component Breakdown](#component-breakdown)
- [Data Flow](#data-flow)
- [Authentication & Authorization](#authentication--authorization)
- [AI/ML Pipeline](#aiml-pipeline)
- [Fairness & Bias Prevention](#fairness--bias-prevention)
- [Background Processing](#background-processing)
- [Deployment Architecture](#deployment-architecture)
- [Service Communication](#service-communication)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────────────┐   │
│  │ Browser  │  │ Electron App │  │ External API Consumers  │   │
│  │(Frontend)│  │  (Desktop)   │  │  (Webhooks / Postman)   │   │
│  └────┬─────┘  └──────┬───────┘  └───────────┬─────────────┘   │
└───────┼────────────────┼──────────────────────┼─────────────────┘
        │ HTTP/WS        │ HTTP                 │ REST API
        ▼                ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Flask Backend (app.py)                         │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  API Routes (Blueprints)                   │ │
│  │  auth │ jobs │ candidates │ ai-interview │ assessments     │ │
│  │  admin │ dashboard │ audit │ dsr │ email │ webhooks        │ │
│  └──────────────────────┬─────────────────────────────────────┘ │
│                         │                                       │
│  ┌──────────┐  ┌────────┴───────┐  ┌───────────────────────┐   │
│  │ Security │  │    Services    │  │    Matching Engine    │   │
│  │  - RBAC  │  │  - AI/ML      │  │  - Decision engine    │   │
│  │  - JWT   │  │  - Email      │  │  - Fresher scoring    │   │
│  │  - Enc.  │  │  - Fairness   │  │  - Experienced score  │   │
│  │  - Rate  │  │  - Analytics  │  │  - Eligibility check  │   │
│  └──────────┘  └───────┬────────┘  └───────────────────────┘   │
│                        │                                        │
│  ┌─────────────────────┼──────────────────────────────────────┐ │
│  │           Background Workers (Celery + Redis)              │ │
│  │  - Resume processing   - Email dispatch                    │ │
│  │  - Score computation   - Webhook delivery                  │ │
│  │  - Notification queue  - Dead letter queue                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────┬──────────────────┬──────────────────┬──────────────┘
             │                  │                  │
             ▼                  ▼                  ▼
     ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐
     │  MongoDB 7.0 │  │   Redis 7    │  │  External Services │
     │  - Users     │  │  - Cache     │  │  - Brevo SMTP      │
     │  - Jobs      │  │  - Sessions  │  │  - LinkedIn OAuth   │
     │  - Scores    │  │  - Queue     │  │  - Google OAuth     │
     │  - Audits    │  │  - Rate lim. │  │  - Sentry           │
     └──────────────┘  └──────────────┘  └────────────────────┘
             ▲                                     ▲
             │              Microservices           │
     ┌───────┴──────────────────────────────┐      │
     │  ┌──────────────┐  ┌──────────────┐  │      │
     │  │ AIF360       │  │ ML Service   │  ├──────┘
     │  │ Fairness API │  │ (Heavy ML)   │  │
     │  └──────────────┘  └──────────────┘  │
     └──────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Backend (`backend/`)

The core application, built with **Flask 3.0** using the **app factory pattern**.

#### Routes (14 Blueprints)

| Route Module | Prefix | Responsibility |
|---|---|---|
| `auth_routes` | `/api/auth` | Registration, login, JWT token management |
| `google_oauth_routes` | `/api/auth` | Google OAuth2 SSO flow |
| `job_routes` | `/api/jobs` | Job posting CRUD, search, filtering |
| `candidate_routes` | `/api/candidates` | Candidate profiles, applications, status tracking |
| `company_routes` | `/api/company` | Company profile management |
| `assessment_routes` | `/api/assessments` | Skill quizzes and coding assessments |
| `ai_interview_routes` | `/api/ai-interview` | AI interview v1 — question generation and evaluation |
| `ai_interview_routes_v2` | `/api/ai-interview-v2` | AI interview v2 — LinkedIn integration, dynamic questions, fresher scoring |
| `interview_routes` | `/api/interviews` | Interview scheduling and management |
| `admin_routes` | `/api/admin` | Admin panel, user management, system settings |
| `dashboard_routes` | `/api/dashboard` | Analytics, metrics, reporting |
| `audit_routes` | `/api/audit` | Fairness audits, compliance reports |
| `dsr_routes` | `/api/dsr` | GDPR Data Subject Requests |
| `email_preferences_routes` | `/api/email` | Email opt-in/out preferences |
| `video_interview_routes` | `/api/video-interview` | Video interview infrastructure |
| `webhook_routes` | `/api/webhooks` | External webhook integrations |

#### Services (24 Modules)

| Category | Modules | Description |
|---|---|---|
| **AI/ML** | `ml_matching_service`, `ranking_service`, `advanced_nlp_service` | Candidate scoring, semantic matching, NLP |
| **AI Interview** | `ai_interviewer_service`, `ai_interviewer_service_v2`, `question_banks` | Dynamic question generation, evaluation |
| **Resume** | `resume_parser_service`, `resume_upload_service` | PDF/DOCX parsing, file handling |
| **Fairness** | `fairness_service`, `fairness_engine`, `fairness_audit_service`, `fairness_proxy` | Bias detection, metrics, AIF360 integration |
| **Transparency** | `explainability_service`, `transparency_service` | XAI explanations, transparency reports |
| **GDPR** | `anonymization_service` | PII redaction, data anonymization |
| **Communication** | `email_service`, `email_templates`, `websocket_service` | Email dispatch, real-time notifications |
| **Analytics** | `analytics_service` | Dashboard data, trend analysis |
| **Scheduling** | `interview_scheduling_service` | Calendar coordination |
| **Integration** | `linkedin_career_service`, `ml_service_client` | LinkedIn API, ML microservice client |
| **Video** | `video_interview_service` | Video interview management |
| **Caching** | `cache_service` | Redis-backed response caching |

#### Models (MongoDB Collections)

| Model | Collection | Key Fields |
|---|---|---|
| `User` | `users` | email, password_hash, role, profile |
| `Job` | `jobs` | title, description, requirements, company_id |
| `Assessment` | `assessments` | questions, scoring_criteria, job_id |
| `Fairness` | `fairness_metrics` | demographic_parity, equal_opportunity, timestamps |
| `CandidateScoringLog` | `scoring_logs` | candidate_id, job_id, scores, explanation |

#### Security Layer

| Module | Feature |
|---|---|
| `rbac.py` | Role-based access control (Candidate, Company, Admin) |
| `encryption.py` | AES encryption for sensitive data at rest |
| `rate_limiter.py` | Per-endpoint rate limiting via Redis |
| `file_security.py` | Upload validation, virus scanning hooks, file type whitelist |

Global security headers: `HSTS`, `CSP`, `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`.

---

### 2. Frontend (`frontend/`)

A **vanilla HTML/CSS/JS** single-page-style application served as static files by Flask.

| Page | Purpose |
|---|---|
| `index.html` | Landing page, login, registration |
| `interview_room.html` | Live AI/video interview room |
| `questions.html` / `quizzes.html` / `take-quiz.html` | Assessment interface |
| `forgot-password.html` / `reset-password.html` | Password recovery |
| `email-preferences.html` | Email notification settings |
| `accessibility-audit.html` | Accessibility compliance report |

**Key JS modules:** `app.js` (SPA router), `api.js` (API client), `admin.js`, `candidate.js`, `company.js` (role-specific logic), `security-utils.js` (XSS prevention), `a11y.js` (accessibility).

---

### 3. Microservices

#### AIF360 Fairness Service (`aif360-service/`)

A standalone Flask microservice providing advanced fairness analysis using IBM's AIF360 library. Deployed independently to isolate heavy dependencies.

- **Endpoint:** Fairness metrics computation
- **Communication:** HTTP REST (called via `fairness_proxy` service in main backend)

#### ML Service (`ml-service/`)

A standalone Flask microservice for computationally intensive ML operations:

- Resume parsing with heavy NLP models
- Skill extraction and taxonomy matching
- Advanced analytics computations
- Fairness metric calculations

---

### 4. Desktop App (`desktop/`)

An **Electron** wrapper that packages the web application as a native desktop app.

- `main.js` — Electron main process
- `preload.js` — Secure context bridge
- `renderer.js` — Renderer process logic

---

### 5. Configuration (`config/`)

| File | Purpose |
|---|---|
| `config.py` | Flask app configuration (dev/prod/test) |
| `scoring_config.py` | ML scoring weights and thresholds |
| `skill_ontology.py` / `skill_ontology.json` | Skill taxonomy and synonyms |

---

## Data Flow

### Resume Upload → Job Matching

```
1. Candidate uploads resume (PDF/DOCX)
       │
       ▼
2. File security validation (type check, size limit, malware scan hook)
       │
       ▼
3. Resume parser extracts text, skills, experience, education
       │  (spaCy NLP + PyPDF2/pdfplumber + python-docx)
       │
       ▼
4. Candidate profile stored in MongoDB
       │
       ▼
5. When candidate applies to a job:
       │
       ▼
6. ML matching engine computes score:
       ├── Skill match (keyword + semantic via Sentence-BERT)
       ├── Experience alignment
       ├── Education relevance
       └── Fresher vs Experienced scoring path
       │
       ▼
7. Fairness engine evaluates for bias:
       ├── Demographic parity check
       ├── Equal opportunity check
       └── Score adjustment if bias detected
       │
       ▼
8. Explainability service generates reasoning
       │
       ▼
9. Final score + explanation stored in scoring_logs
       │
       ▼
10. Company views ranked candidates on dashboard
```

### AI Interview Flow

```
1. Company configures interview for a job posting
       │
       ▼
2. Candidate enters interview room (WebSocket connection)
       │
       ▼
3. AI Interview Engine v2:
       ├── Loads job requirements
       ├── Checks candidate's LinkedIn data (if available)
       ├── Generates dynamic questions from question banks
       └── Adapts difficulty based on candidate profile
       │
       ▼
4. Real-time question delivery via WebSocket
       │
       ▼
5. Candidate responds (text/audio)
       │
       ▼
6. AI evaluates responses:
       ├── Relevance scoring
       ├── Technical accuracy
       ├── Communication assessment
       └── Composite score calculation
       │
       ▼
7. Results stored and added to candidate's overall score
```

---

## Authentication & Authorization

```
┌─────────────────────────────────────────────────┐
│                 Auth Flow                         │
│                                                   │
│  1. Login → POST /api/auth/login                 │
│     ├── Email + Password (bcrypt)                │
│     ├── Google OAuth (redirect flow)             │
│     └── LinkedIn OAuth (redirect flow)           │
│                                                   │
│  2. JWT Access Token returned                    │
│     ├── Short-lived (configurable, default 1hr)  │
│     └── Stored client-side                       │
│                                                   │
│  3. Every API request includes:                  │
│     Authorization: Bearer <token>                │
│                                                   │
│  4. RBAC Middleware checks:                      │
│     ├── Token validity                           │
│     ├── User role (candidate/company/admin)      │
│     └── Endpoint permission                      │
└─────────────────────────────────────────────────┘

Roles:
  - Candidate: Job search, apply, interview, assessments
  - Company: Post jobs, view candidates, manage interviews
  - Admin: Full system access, user management, audits
```

---

## AI/ML Pipeline

```
                    ┌─────────────────────┐
                    │    Input Sources     │
                    │  Resume │ Job Desc.  │
                    └────────┬────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌──────────────┐ ┌──────────┐ ┌──────────────┐
     │   spaCy NLP  │ │ Skill    │ │ Sentence-    │
     │ Entity Recog.│ │ Ontology │ │ BERT Embed.  │
     └──────┬───────┘ └────┬─────┘ └──────┬───────┘
            │              │              │
            ▼              ▼              ▼
     ┌─────────────────────────────────────────┐
     │         Matching / Scoring Engine        │
     │  ┌─────────┐ ┌───────────┐ ┌─────────┐  │
     │  │ Keyword │ │ Semantic  │ │Composite│  │
     │  │ Match   │ │ Similarity│ │ Score   │  │
     │  └─────────┘ └───────────┘ └─────────┘  │
     └──────────────────┬──────────────────────┘
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
     ┌──────────────┐   ┌──────────────────┐
     │   Fairness   │   │  Explainability  │
     │   Auditor    │   │    Generator     │
     └──────────────┘   └──────────────────┘
```

Key ML libraries:
- **scikit-learn** — Classification, clustering, scoring models
- **Sentence-Transformers** — Semantic similarity via SBERT embeddings
- **PyTorch** — Deep learning backend for transformer models
- **spaCy** — Named entity recognition, skill extraction
- **Fairlearn** — Fairness metrics and bias mitigation
- **pandas/numpy** — Data processing and analysis

---

## Fairness & Bias Prevention

The system implements a **multi-layered fairness architecture**:

| Layer | Component | Purpose |
|---|---|---|
| 1. Pre-processing | `anonymization_service` | Remove PII before scoring |
| 2. In-processing | `fairness_engine` | Apply constraints during scoring |
| 3. Post-processing | `fairness_audit_service` | Audit scores for disparate impact |
| 4. External | `aif360-service` (microservice) | Advanced fairness metrics via IBM AIF360 |
| 5. Reporting | `transparency_service` | Generate compliance reports |

Metrics monitored:
- **Demographic Parity** — Score distributions across demographic groups
- **Equal Opportunity** — True positive rates across groups
- **Disparate Impact Ratio** — Threshold-based bias detection

---

## Background Processing

```
┌──────────────┐     ┌─────────────┐     ┌──────────────────┐
│ Flask App    │────▶│  Redis 7    │────▶│  Celery Workers  │
│ (Producer)   │     │  (Broker)   │     │  (Consumers)     │
└──────────────┘     └─────────────┘     └──────┬───────────┘
                                                │
                          ┌─────────────────────┼──────────────┐
                          ▼                     ▼              ▼
                   ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
                   │ Email Tasks │  │ Resume Tasks │  │ Webhook Tasks│
                   │ - Send mail │  │ - Parse      │  │ - Deliver    │
                   │ - Templates │  │ - Score      │  │ - Retry      │
                   │ - Bulk      │  │ - Notify     │  │ - DLQ        │
                   └─────────────┘  └──────────────┘  └──────────────┘
```

Celery tasks (in `backend/tasks/`):
- `email_tasks.py` — Async email delivery
- `resume_tasks.py` — Background resume processing
- `notification_tasks.py` — Push notifications
- `webhook_tasks.py` — Webhook delivery with retry
- `dlq_tasks.py` — Dead letter queue handling

Monitoring via **Flower** web UI at port 5555.

---

## Deployment Architecture

### Docker Compose (Full Stack)

```
docker-compose.yml
├── backend       (Flask + Gunicorn, port 5000)
├── mongodb       (MongoDB 7.0, port 27017)
├── redis         (Redis 7, port 6379)
├── celery-worker (Celery consumer)
└── flower        (Monitoring, port 5555)
```

### Cloud Platforms

| Platform | Type | Config |
|---|---|---|
| Railway | PaaS | `railway.json`, `Procfile` |
| Render | PaaS | `render.yaml` |
| Fly.io | PaaS | `fly.toml` |
| Vercel | Serverless (frontend) | `vercel.json` |
| Netlify | Serverless (frontend) | `netlify.toml`, `netlify/functions/` |
| Google Cloud Build | CI/Build | `cloudbuild.yaml` |

### CI/CD (GitHub Actions)

| Workflow | Trigger | Purpose |
|---|---|---|
| `ci.yml` | Push / PR | Lint, test, build |
| `release-candidate.yml` | Tag | Pre-release build and deploy |
| `release.yml` | Release | Production deployment |

---

## Service Communication

```
┌───────────────────┐       REST API        ┌──────────────────┐
│   Main Backend    │◄─────────────────────▶│   AIF360 Service │
│   (Flask)         │   /api/fairness/*     │   (Flask)        │
└─────────┬─────────┘                       └──────────────────┘
          │
          │         REST API        ┌──────────────────┐
          ├────────────────────────▶│   ML Service     │
          │   /api/ml/*            │   (Flask)        │
          │                        └──────────────────┘
          │
          │         SMTP            ┌──────────────────┐
          ├────────────────────────▶│   Brevo SMTP     │
          │                        └──────────────────┘
          │
          │         OAuth2          ┌──────────────────┐
          ├────────────────────────▶│   Google / LI    │
          │                        └──────────────────┘
          │
          │         HTTPS           ┌──────────────────┐
          └────────────────────────▶│   Sentry         │
                                   └──────────────────┘
```

All inter-service communication uses **HTTP REST** with JSON payloads. The main backend acts as the orchestrator, calling microservices as needed and aggregating results.

---

## Database Schema (MongoDB)

### Key Collections

| Collection | Purpose | Indexed Fields |
|---|---|---|
| `users` | User accounts & profiles | `email` (unique), `role` |
| `jobs` | Job postings | `company_id`, `status`, `created_at` |
| `applications` | Job applications | `candidate_id`, `job_id`, `status` |
| `assessments` | Quizzes & tests | `job_id`, `type` |
| `scoring_logs` | Score audit trail | `candidate_id`, `job_id`, `timestamp` |
| `fairness_metrics` | Fairness audit data | `job_id`, `timestamp` |
| `interviews` | Interview records | `candidate_id`, `job_id`, `status` |

---

*This document reflects the system as of v1.0.0. Updated February 2026.*
