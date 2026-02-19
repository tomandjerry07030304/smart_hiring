import re

from config.scoring_config import ScoringConfig
from config.skill_ontology import SKILL_DATABASE

# ML libraries not available in Render free tier (size constraints)
# Simplified matching without scikit-learn
def _get_tfidf_vectorizer():
    return None

def _get_cosine_similarity():
    return None

# Gap 10: Skills loaded from unified skill_ontology.json (single source of truth)
SKILLS_MASTER = sorted(SKILL_DATABASE)

def extract_skills(text):
    """Extract skills from text using dictionary matching"""
    if not text:
        print("⚠️ extract_skills: Empty text provided")
        return []
    
    print(f"🔍 extract_skills: Processing text of length {len(text)}")
    txt = text.lower()
    found = []
    
    for skill in SKILLS_MASTER:
        # Use word boundary for accurate matching
        if re.search(r'\b' + re.escape(skill) + r'\b', txt):
            found.append(skill)
    
    unique_skills = list(set(found))  # Remove duplicates
    print(f"✅ extract_skills: Found {len(unique_skills)} unique skills from {len(found)} total matches")
    
    return unique_skills

def calculate_tfidf_similarity(job_text, resume_text):
    """Calculate TF-IDF cosine similarity between job and resume"""
    try:
        # Lazy load sklearn
        TfidfVectorizer = _get_tfidf_vectorizer()
        cosine_similarity = _get_cosine_similarity()
        
        texts = [job_text, resume_text]
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
        return float(similarity)
    except Exception as e:
        print(f"TF-IDF error: {e}")
        return 0.0

def calculate_skill_match(job_skills, resume_skills):
    """Calculate skill match percentage"""
    if not job_skills:
        return 0.0
    
    job_set = set([s.lower() for s in job_skills])
    resume_set = set([s.lower() for s in resume_skills])
    
    matched = job_set.intersection(resume_set)
    match_fraction = len(matched) / len(job_set)
    
    return float(match_fraction)

def compute_overall_score(tfidf_score, skill_match, cci_score=None, sim_weight=None, skill_weight=None, cci_weight=None):
    """
    Compute overall candidate score.
    
    Weights default to canonical values from ScoringConfig (Gap 6 fix).
    Explicit overrides are accepted for backward compatibility but
    new callers should rely on the defaults.
    
    Args:
        tfidf_score: TF-IDF similarity score (0-1)
        skill_match: Skill match fraction (0-1)
        cci_score: Career Consistency Index (0-100), optional
        sim_weight: Weight for similarity (default: canonical)
        skill_weight: Weight for skill match (default: canonical)
        cci_weight: Weight for CCI (default: canonical)
    """
    if cci_score is None:
        # No CCI available — redistribute proportionally
        w = ScoringConfig.weights_for_without_cci('similarity', 'skills')
        sw = sim_weight if sim_weight is not None else w['similarity']
        skw = skill_weight if skill_weight is not None else w['skills']
        score = (sw * tfidf_score + skw * skill_match) * 100
    else:
        # Full 3-component scoring
        w = ScoringConfig.weights_for('similarity', 'skills', 'cci')
        sw = sim_weight if sim_weight is not None else w['similarity']
        skw = skill_weight if skill_weight is not None else w['skills']
        cw = cci_weight if cci_weight is not None else w['cci']
        cci_normalized = cci_score / 100.0
        score = (sw * tfidf_score + skw * skill_match + cw * cci_normalized) * 100
    
    return round(float(score), 2)

def get_decision_from_score(score):
    """Get hiring decision based on score"""
    if score >= 75:
        return "Hire"
    elif score >= 50:
        return "Review"
    else:
        return "Reject"

def analyze_candidate(job_description, job_skills, resume_text, resume_skills, cci_score=None):
    """
    Comprehensive candidate analysis
    
    Returns:
        dict with scores, decision, matched skills, and recommendations
    """
    # Calculate scores
    tfidf_score = calculate_tfidf_similarity(job_description, resume_text)
    skill_match = calculate_skill_match(job_skills, resume_skills)
    overall_score = compute_overall_score(tfidf_score, skill_match, cci_score)
    decision = get_decision_from_score(overall_score)
    
    # Find matched and missing skills
    job_set = set([s.lower() for s in job_skills])
    resume_set = set([s.lower() for s in resume_skills])
    matched_skills = list(job_set.intersection(resume_set))
    missing_skills = list(job_set - resume_set)
    
    # Generate recommendations
    recommendations = []
    if skill_match < 0.5:
        recommendations.append(f"Improve skills in: {', '.join(missing_skills[:5])}")
    if cci_score and cci_score < 60:
        recommendations.append("Consider building more consistent career progression")
    if tfidf_score < 0.4:
        recommendations.append("Tailor resume to better match job requirements")
    
    return {
        'tfidf_score': round(tfidf_score, 3),
        'skill_match': round(skill_match, 3),
        'cci_score': cci_score,
        'overall_score': overall_score,
        'decision': decision,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'recommendations': recommendations
    }
