# Technology Stack

## Core Backend
- **Language:** Python 3.x
- **Framework:** Flask (v3.0.0)
- **Production Server:** Gunicorn with Eventlet worker class for concurrency.
- **API Documentation:** APISpec with Marshmallow for schema validation.

## Frontend
- **Architecture:** Monolithic architecture where Flask serves static assets.
- **Technologies:** Vanilla HTML5, CSS3 (including custom UI enhancements), and modern JavaScript (ES6+).
- **Style:** Clean, minimalist design with a focus on data visualization and accessibility.

## Data Storage & Queuing
- **Primary Database:** MongoDB (NoSQL) for flexible candidate and job data storage.
- **Task Queue & Broker:** Celery with Redis for asynchronous processing (e.g., resume parsing, email dispatch).
- **Caching:** Redis for session management and performance optimization.

## Machine Learning & NLP
- **Semantic Matching:** Sentence-Transformers (Sentence-BERT) for high-accuracy candidate-to-job matching.
- **Fairness Evaluation:** Fairlearn for bias detection and mitigation in recruitment algorithms.
- **NLP & Parsing:** Spacy for Named Entity Recognition (NER); PyPDF2 and python-docx for document extraction.
- **General ML:** Scikit-learn and NumPy for data processing and ranking algorithms.

## Security & DevOps
- **Authentication:** Flask-JWT-Extended for stateless token-based security.
- **Encryption:** Flask-Bcrypt for password hashing; Cryptography library for sensitive data.
- **MFA:** PyOTP and qrcode for Multi-Factor Authentication.
- **Environment Management:** Python-dotenv for configuration; Git for version control.
- **Monitoring:** Sentry-sdk for error tracking; Flower for Celery task monitoring.
