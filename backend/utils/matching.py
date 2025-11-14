import re
import numpy as np

# Lazy imports for heavy libraries
def _get_tfidf_vectorizer():
    from sklearn.feature_extraction.text import TfidfVectorizer
    return TfidfVectorizer

def _get_cosine_similarity():
    from sklearn.metrics.pairwise import cosine_similarity
    return cosine_similarity

# Master skills list (can be extended)
SKILLS_MASTER = [
    "python", "sql", "java", "c++", "c#", "javascript", "react", "node", "html", "css",
    "machine learning", "deep learning", "nlp", "pandas", "numpy", "tensorflow", "keras",
    "docker", "kubernetes", "aws", "azure", "git", "tableau", "powerbi", "excel", "matlab",
    "spark", "hadoop", "scikit-learn", "mongodb", "postgresql", "mysql", "redis",
    "angular", "vue", "typescript", "flask", "django", "fastapi", "rest api", "graphql",
    "ci/cd", "jenkins", "github actions", "agile", "scrum", "microservices", "devops"
]

def extract_skills(text):
    """Extract skills from text using dictionary matching"""
    if not text:
        return []
    
    txt = text.lower()
    found = []
    
    for skill in SKILLS_MASTER:
        # Use word boundary for accurate matching
        if re.search(r'\b' + re.escape(skill) + r'\b', txt):
            found.append(skill)
    
    return list(set(found))  # Remove duplicates

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

def compute_overall_score(tfidf_score, skill_match, cci_score=None, sim_weight=0.5, skill_weight=0.3, cci_weight=0.2):
    """
    Compute overall candidate score
    
    Args:
        tfidf_score: TF-IDF similarity score (0-1)
        skill_match: Skill match fraction (0-1)
        cci_score: Career Consistency Index (0-100), optional
        sim_weight: Weight for similarity
        skill_weight: Weight for skill match
        cci_weight: Weight for CCI
    """
    if cci_score is None:
        # If no CCI, redistribute weight
        sim_weight = 0.6
        skill_weight = 0.4
        cci_weight = 0.0
        score = (sim_weight * tfidf_score + skill_weight * skill_match) * 100
    else:
        # Normalize CCI to 0-1
        cci_normalized = cci_score / 100.0
        score = (sim_weight * tfidf_score + skill_weight * skill_match + cci_weight * cci_normalized) * 100
    
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
