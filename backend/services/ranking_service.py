"""
ML-Powered Candidate Ranking Service
Provides intelligent candidate scoring and ranking using machine learning
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re

# Try to import ML libraries, fall back to basic scoring if not available
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import MinMaxScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ scikit-learn not available. Using basic ranking. Install with: pip install scikit-learn")


class MLCandidateRanker:
    """
    Machine Learning-based Candidate Ranking System
    
    Features:
    - TF-IDF based resume-job matching
    - Skills-based scoring with importance weights
    - Experience level matching
    - Education qualification scoring
    - Career consistency analysis
    - Combined ML score with explainability
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english') if ML_AVAILABLE else None
        self.scaler = MinMaxScaler() if ML_AVAILABLE else None
        
        # Feature weights (can be tuned based on historical data)
        self.weights = {
            'skills_match': 0.35,
            'experience': 0.25,
            'education': 0.15,
            'resume_similarity': 0.20,
            'career_consistency': 0.05
        }
    
    def rank_candidates(self, candidates: List[Dict], job: Dict) -> List[Dict]:
        """
        Rank candidates for a job using ML-based scoring
        
        Args:
            candidates: List of candidate profiles with resumes
            job: Job posting with requirements
        
        Returns:
            List of candidates with ML scores, sorted by rank
        """
        if not candidates:
            return []
        
        scored_candidates = []
        
        for candidate in candidates:
            score_details = self._calculate_ml_score(candidate, job)
            
            candidate_with_score = {
                **candidate,
                'ml_score': score_details['overall_score'],
                'score_breakdown': score_details,
                'rank_explanation': self._generate_explanation(score_details)
            }
            scored_candidates.append(candidate_with_score)
        
        # Sort by ML score (descending)
        scored_candidates.sort(key=lambda x: x['ml_score'], reverse=True)
        
        # Add rank positions
        for i, candidate in enumerate(scored_candidates, 1):
            candidate['rank'] = i
            candidate['percentile'] = round((len(scored_candidates) - i + 1) / len(scored_candidates) * 100, 1)
        
        return scored_candidates
    
    def _calculate_ml_score(self, candidate: Dict, job: Dict) -> Dict:
        """Calculate comprehensive ML score with breakdown"""
        
        # Extract features
        candidate_skills = set([s.lower() for s in candidate.get('skills', [])])
        job_skills = set([s.lower() for s in job.get('required_skills', [])])
        
        candidate_resume = candidate.get('resume_text', '')
        job_description = job.get('description', '')
        
        candidate_experience = candidate.get('experience_years', 0)
        required_experience = self._parse_experience_requirement(job.get('experience_required', '0'))
        
        candidate_education = candidate.get('education', '').lower()
        required_education = job.get('education_requirement', '').lower()
        
        # Calculate individual scores
        skills_score = self._score_skills_match(candidate_skills, job_skills)
        experience_score = self._score_experience(candidate_experience, required_experience)
        education_score = self._score_education(candidate_education, required_education)
        resume_similarity = self._score_resume_similarity(candidate_resume, job_description)
        career_consistency = candidate.get('cci_score', 50) / 100  # Normalize CCI to 0-1
        
        # Weighted combination
        overall_score = (
            self.weights['skills_match'] * skills_score +
            self.weights['experience'] * experience_score +
            self.weights['education'] * education_score +
            self.weights['resume_similarity'] * resume_similarity +
            self.weights['career_consistency'] * career_consistency
        )
        
        return {
            'overall_score': round(overall_score * 100, 2),  # Convert to 0-100 scale
            'skills_match': round(skills_score * 100, 2),
            'experience': round(experience_score * 100, 2),
            'education': round(education_score * 100, 2),
            'resume_similarity': round(resume_similarity * 100, 2),
            'career_consistency': round(career_consistency * 100, 2),
            'matched_skills': list(candidate_skills.intersection(job_skills)),
            'missing_skills': list(job_skills - candidate_skills)
        }
    
    def _score_skills_match(self, candidate_skills: set, job_skills: set) -> float:
        """Score based on skill match (Jaccard similarity)"""
        if not job_skills:
            return 1.0
        
        intersection = len(candidate_skills.intersection(job_skills))
        union = len(candidate_skills.union(job_skills))
        
        if union == 0:
            return 0.0
        
        # Jaccard similarity
        jaccard = intersection / union
        
        # Boost for high coverage of required skills
        coverage = intersection / len(job_skills)
        
        # Weighted average favoring coverage
        return 0.4 * jaccard + 0.6 * coverage
    
    def _score_experience(self, candidate_exp: float, required_exp: float) -> float:
        """Score based on experience match"""
        if required_exp == 0:
            return 1.0
        
        if candidate_exp >= required_exp:
            # Perfect if meets requirement, slight penalty for overqualification
            excess = candidate_exp - required_exp
            if excess > required_exp * 2:
                return 0.9  # Might be overqualified
            return 1.0
        else:
            # Partial credit for close matches
            ratio = candidate_exp / required_exp
            if ratio >= 0.75:
                return 0.85  # Close enough
            elif ratio >= 0.5:
                return 0.70  # Significant gap but trainable
            else:
                return 0.50  # Major gap
    
    def _score_education(self, candidate_edu: str, required_edu: str) -> float:
        """Score based on education level"""
        education_levels = {
            'phd': 5, 'doctorate': 5,
            'master': 4, 'mba': 4, 'ms': 4, 'ma': 4,
            'bachelor': 3, 'bs': 3, 'ba': 3, 'btech': 3, 'be': 3,
            'associate': 2,
            'high school': 1, 'diploma': 1
        }
        
        # Get education level scores
        candidate_level = 0
        for edu_type, level in education_levels.items():
            if edu_type in candidate_edu:
                candidate_level = max(candidate_level, level)
        
        required_level = 0
        for edu_type, level in education_levels.items():
            if edu_type in required_edu:
                required_level = max(required_level, level)
        
        if required_level == 0:
            return 1.0  # No specific requirement
        
        if candidate_level >= required_level:
            return 1.0  # Meets or exceeds
        elif candidate_level >= required_level - 1:
            return 0.75  # One level below
        else:
            return 0.50  # Significant gap
    
    def _score_resume_similarity(self, resume: str, job_desc: str) -> float:
        """Score based on resume-job description similarity using TF-IDF"""
        if not ML_AVAILABLE or not resume or not job_desc:
            # Fallback to keyword matching
            resume_words = set(resume.lower().split())
            job_words = set(job_desc.lower().split())
            common = len(resume_words.intersection(job_words))
            return min(common / 100, 1.0)  # Cap at 1.0
        
        try:
            # TF-IDF vectorization
            documents = [job_desc, resume]
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            
            # Cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except:
            return 0.5  # Default if TF-IDF fails
    
    def _parse_experience_requirement(self, exp_str: str) -> float:
        """Parse experience requirement from string like '3+ years' or '5-7 years'"""
        if not exp_str:
            return 0.0
        
        # Look for numbers
        numbers = re.findall(r'\d+', str(exp_str))
        if not numbers:
            return 0.0
        
        # Take the first number as minimum requirement
        return float(numbers[0])
    
    def _generate_explanation(self, score_details: Dict) -> str:
        """Generate human-readable explanation of the score"""
        overall = score_details['overall_score']
        
        if overall >= 85:
            rating = "Excellent Match"
        elif overall >= 70:
            rating = "Good Match"
        elif overall >= 55:
            rating = "Fair Match"
        else:
            rating = "Weak Match"
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for category in ['skills_match', 'experience', 'education', 'resume_similarity']:
            score = score_details[category]
            if score >= 75:
                strengths.append(category.replace('_', ' ').title())
            elif score < 60:
                weaknesses.append(category.replace('_', ' ').title())
        
        explanation = f"{rating} ({overall:.1f}%). "
        
        if strengths:
            explanation += f"Strong in: {', '.join(strengths)}. "
        
        if weaknesses:
            explanation += f"Needs improvement in: {', '.join(weaknesses)}."
        
        if score_details['matched_skills']:
            explanation += f" Matched skills: {', '.join(score_details['matched_skills'][:5])}."
        
        return explanation


# Global instance
ml_ranker = MLCandidateRanker()


def rank_candidates_for_job(candidates: List[Dict], job: Dict) -> List[Dict]:
    """
    Main function to rank candidates using ML
    
    Usage:
        ranked = rank_candidates_for_job(candidates, job)
        for candidate in ranked[:10]:  # Top 10
            print(f"{candidate['rank']}. {candidate['name']} - Score: {candidate['ml_score']}")
    """
    return ml_ranker.rank_candidates(candidates, job)


def get_candidate_insights(candidate: Dict, job: Dict) -> Dict:
    """
    Get detailed insights for a single candidate
    
    Returns:
        Dict with ML score, strengths, weaknesses, and recommendations
    """
    score_details = ml_ranker._calculate_ml_score(candidate, job)
    
    return {
        'ml_score': score_details['overall_score'],
        'score_breakdown': score_details,
        'explanation': ml_ranker._generate_explanation(score_details),
        'recommendation': _get_recommendation(score_details),
        'interview_focus_areas': _get_interview_focus(score_details)
    }


def _get_recommendation(score_details: Dict) -> str:
    """Get hiring recommendation based on score"""
    score = score_details['overall_score']
    
    if score >= 85:
        return "Highly Recommended - Schedule interview immediately"
    elif score >= 70:
        return "Recommended - Good candidate, proceed with interview"
    elif score >= 55:
        return "Consider - Review application carefully, may need training"
    else:
        return "Not Recommended - Significant skill gaps"


def _get_interview_focus(score_details: Dict) -> List[str]:
    """Suggest areas to focus on during interview"""
    focus_areas = []
    
    if score_details['skills_match'] < 70:
        focus_areas.append("Assess missing technical skills: " + ", ".join(score_details['missing_skills'][:5]))
    
    if score_details['experience'] < 70:
        focus_areas.append("Verify hands-on experience with relevant technologies")
    
    if score_details['career_consistency'] < 60:
        focus_areas.append("Discuss career progression and job transitions")
    
    if not focus_areas:
        focus_areas.append("Verify depth of expertise in matched skills")
        focus_areas.append("Assess cultural fit and soft skills")
    
    return focus_areas
