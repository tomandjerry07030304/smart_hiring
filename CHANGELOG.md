# Changelog

All notable changes to the Smart Hiring System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Project reorganization: clean folder structure for GitHub
- Comprehensive `.gitignore` covering all non-code, sensitive, and generated files
- `README.md` with setup instructions, tech stack, and project overview
- `CONTRIBUTING.md` with development guidelines
- `CHANGELOG.md` template for version tracking
- `SYSTEM_OVERVIEW.md` with architecture and data flow documentation
- `docs/` folder with `SECURITY.md` and `API_DOCUMENTATION.md`

### Changed
- Moved root-level test scripts to `tests/` directory
- Moved root-level utility scripts to `scripts/` directory
- Organized non-code files (documents, diagrams, archives) into `non-git-files/`

### Removed
- Cleared `__pycache__/` and `.pytest_cache/` build artifacts
- Removed stray notebook from `backend/routes/`

---

## [1.0.0] — 2026-02-19

### Added
- Flask 3.0 backend with app factory pattern
- MongoDB database integration via PyMongo
- Redis + Celery async task queue
- JWT authentication with Google and LinkedIn OAuth
- Role-Based Access Control (Candidate, Company, Admin)
- AI resume parsing (spaCy, PyPDF2, pdfplumber)
- ML candidate-job matching (Sentence-BERT, scikit-learn)
- AI interview engine (v1 and v2) with dynamic question generation
- Fairness engine with Fairlearn + AIF360 microservice
- Explainability and transparency reporting
- GDPR compliance (DSR, PII anonymization, audit logging)
- Transactional email via Brevo SMTP
- Analytics dashboard
- Real-time WebSocket communication
- Video interview support
- Vanilla HTML/CSS/JS frontend served by Flask
- Electron desktop application
- Docker Compose full-stack deployment
- GitHub Actions CI/CD pipelines
- Multi-platform deployment support (Railway, Render, Fly.io, Vercel, Netlify)

---

<!--
## [X.Y.Z] — YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Features to be removed in upcoming releases

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements or vulnerability fixes
-->
