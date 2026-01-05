"""
ML Microservice for Smart Hiring System
========================================
Handles computationally heavy operations:
- Resume parsing (PDF/DOCX)
- Skill extraction
- Dashboard analytics
- Fairness calculations

Deploy on: Railway.app, Fly.io, or any platform with higher memory limits
"""

import os
import io
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np

# Resume parsing
try:
    from PyPDF2 import PdfReader
    from docx import Document
    RESUME_PARSING_AVAILABLE = True
except ImportError:
    RESUME_PARSING_AVAILABLE = False

# ML
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Service configuration
SERVICE_SECRET = os.getenv('ML_SERVICE_SECRET', 'your-secret-key')

def verify_request():
    """Verify request comes from main backend"""
    token = request.headers.get('X-Service-Token')
    if token != SERVICE_SECRET:
        return False
    return True

# ==================== HEALTH CHECK ====================
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'ml-microservice',
        'features': {
            'resume_parsing': RESUME_PARSING_AVAILABLE,
            'ml_scoring': ML_AVAILABLE,
            'analytics': True
        }
    })

# ==================== RESUME PARSING ====================
@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    """Parse resume file and extract text"""
    if not RESUME_PARSING_AVAILABLE:
        return jsonify({'error': 'Resume parsing not available'}), 503
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    filename = file.filename.lower()
    
    try:
        file_data = file.read()
        
        if filename.endswith('.pdf'):
            text = extract_pdf_text(file_data)
        elif filename.endswith('.docx'):
            text = extract_docx_text(file_data)
        else:
            text = file_data.decode('utf-8', errors='ignore')
        
        # Extract skills
        skills = extract_skills(text)
        
        return jsonify({
            'success': True,
            'text': text,
            'text_length': len(text),
            'skills': skills,
            'skills_count': len(skills)
        })
    except Exception as e:
        logger.error(f"Resume parsing error: {e}")
        return jsonify({'error': str(e)}), 500

def extract_pdf_text(file_data):
    """Extract text from PDF"""
    reader = PdfReader(io.BytesIO(file_data))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_docx_text(file_data):
    """Extract text from DOCX"""
    doc = Document(io.BytesIO(file_data))
    return "\n".join([para.text for para in doc.paragraphs])

# ==================== SKILL EXTRACTION ====================
SKILLS_DATABASE = [
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
    'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform',
    'git', 'linux', 'agile', 'scrum', 'rest', 'graphql', 'microservices',
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas',
    'numpy', 'scikit-learn', 'nlp', 'computer vision', 'data analysis'
]

def extract_skills(text):
    """Extract skills from text using keyword matching"""
    text_lower = text.lower()
    found_skills = []
    for skill in SKILLS_DATABASE:
        if skill in text_lower:
            found_skills.append(skill)
    return list(set(found_skills))

@app.route('/api/extract-skills', methods=['POST'])
def api_extract_skills():
    """Extract skills from provided text"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    skills = extract_skills(text)
    return jsonify({
        'success': True,
        'skills': skills,
        'count': len(skills)
    })

# ==================== MATCHING & SCORING ====================
@app.route('/api/calculate-match', methods=['POST'])
def calculate_match():
    """Calculate job-candidate match score"""
    if not ML_AVAILABLE:
        return jsonify({'error': 'ML not available'}), 503
    
    data = request.get_json()
    job_text = data.get('job_description', '')
    resume_text = data.get('resume_text', '')
    job_skills = data.get('job_skills', [])
    candidate_skills = data.get('candidate_skills', [])
    
    # TF-IDF similarity
    tfidf_score = calculate_tfidf_similarity(job_text, resume_text)
    
    # Skill match
    skill_match = calculate_skill_match(job_skills, candidate_skills)
    
    # Overall score
    overall = 0.5 * skill_match + 0.5 * tfidf_score
    
    matched = list(set(job_skills) & set(candidate_skills))
    missing = list(set(job_skills) - set(candidate_skills))
    
    return jsonify({
        'success': True,
        'overall_score': round(overall, 3),
        'tfidf_score': round(tfidf_score, 3),
        'skill_match_score': round(skill_match, 3),
        'matched_skills': matched,
        'missing_skills': missing
    })

def calculate_tfidf_similarity(text1, text2):
    """Calculate TF-IDF cosine similarity"""
    if not text1 or not text2:
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
        return float(similarity)
    except:
        return 0.0

def calculate_skill_match(job_skills, candidate_skills):
    """Calculate skill match percentage"""
    if not job_skills:
        return 0.0
    job_set = set([s.lower() for s in job_skills])
    candidate_set = set([s.lower() for s in candidate_skills])
    matched = job_set.intersection(candidate_set)
    return len(matched) / len(job_set)

# ==================== ANALYTICS ====================
@app.route('/api/analytics/stats', methods=['POST'])
def get_analytics():
    """Calculate analytics from provided data"""
    data = request.get_json()
    
    try:
        # Convert to DataFrame
        applications = pd.DataFrame(data.get('applications', []))
        
        if applications.empty:
            return jsonify({
                'total_applications': 0,
                'avg_score': 0,
                'score_distribution': {}
            })
        
        # Calculate stats
        stats = {
            'total_applications': len(applications),
            'avg_score': float(applications['score'].mean()) if 'score' in applications.columns else 0,
            'score_distribution': applications['score'].describe().to_dict() if 'score' in applications.columns else {}
        }
        
        return jsonify({'success': True, **stats})
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== FAIRNESS METRICS ====================
@app.route('/api/fairness/evaluate', methods=['POST'])
def evaluate_fairness():
    """Calculate fairness metrics"""
    data = request.get_json()
    
    try:
        applications = pd.DataFrame(data.get('applications', []))
        protected_attr = data.get('protected_attribute', 'gender')
        
        if applications.empty or protected_attr not in applications.columns:
            return jsonify({'error': 'Invalid data'}), 400
        
        # Group by protected attribute
        groups = applications.groupby(protected_attr)
        
        # Calculate selection rates per group
        selection_rates = {}
        for name, group in groups:
            if 'decision' in group.columns:
                rate = group['decision'].mean()
            elif 'score' in group.columns:
                rate = (group['score'] >= 0.5).mean()
            else:
                rate = 0.5
            selection_rates[str(name)] = float(rate)
        
        # Demographic parity
        rates = list(selection_rates.values())
        dp_diff = max(rates) - min(rates) if rates else 0
        
        # Disparate impact
        di_ratio = min(rates) / max(rates) if max(rates) > 0 else 1.0
        
        return jsonify({
            'success': True,
            'fairness_score': round((1 - dp_diff) * 100, 1),
            'metrics': {
                'demographic_parity': {
                    'difference': round(dp_diff, 3),
                    'passed': dp_diff < 0.1
                },
                'disparate_impact': {
                    'ratio': round(di_ratio, 3),
                    'passed': di_ratio >= 0.8
                }
            },
            'selection_rates': selection_rates
        })
    except Exception as e:
        logger.error(f"Fairness evaluation error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    logger.info(f"🚀 ML Microservice starting on port {port}")
    logger.info(f"   Resume Parsing: {'✅' if RESUME_PARSING_AVAILABLE else '❌'}")
    logger.info(f"   ML Scoring: {'✅' if ML_AVAILABLE else '❌'}")
    app.run(host='0.0.0.0', port=port, debug=False)
