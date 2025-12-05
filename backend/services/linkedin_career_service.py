"""
LinkedIn Integration Service for Career Consistency Verification
Validates candidate career history through LinkedIn API and calculates social proof score
"""

import os
import requests
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
import re
from requests_oauthlib import OAuth2Session


# LinkedIn API Configuration
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_API_BASE = "https://api.linkedin.com/v2"

# Required scopes
LINKEDIN_SCOPES = ['r_liteprofile', 'r_emailaddress', 'w_member_social']


class LinkedInService:
    """Service for LinkedIn OAuth and career verification"""
    
    def __init__(self):
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:5000/api/auth/linkedin/callback')
        
    def get_authorization_url(self, state: str) -> str:
        """
        Generate LinkedIn OAuth authorization URL
        
        Args:
            state: Random state string for CSRF protection
        
        Returns:
            Authorization URL to redirect user to
        """
        oauth = OAuth2Session(
            self.client_id,
            redirect_uri=self.redirect_uri,
            scope=LINKEDIN_SCOPES,
            state=state
        )
        authorization_url, state = oauth.authorization_url(LINKEDIN_AUTH_URL)
        return authorization_url
    
    def get_access_token(self, code: str) -> Optional[str]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from LinkedIn callback
        
        Returns:
            Access token or None if failed
        """
        try:
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(LINKEDIN_TOKEN_URL, data=data)
            response.raise_for_status()
            
            return response.json().get('access_token')
        except Exception as e:
            print(f"❌ LinkedIn token error: {str(e)}")
            return None
    
    def get_profile(self, access_token: str) -> Optional[Dict]:
        """
        Fetch user's LinkedIn profile
        
        Args:
            access_token: LinkedIn access token
        
        Returns:
            Profile data dictionary or None
        """
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Get basic profile
            profile_response = requests.get(
                f"{LINKEDIN_API_BASE}/me",
                headers=headers
            )
            profile_response.raise_for_status()
            profile = profile_response.json()
            
            # Get email
            email_response = requests.get(
                f"{LINKEDIN_API_BASE}/emailAddress?q=members&projection=(elements*(handle~))",
                headers=headers
            )
            email_response.raise_for_status()
            email_data = email_response.json()
            
            # Extract email
            email = None
            if email_data.get('elements'):
                email = email_data['elements'][0].get('handle~', {}).get('emailAddress')
            
            return {
                'id': profile.get('id'),
                'first_name': profile.get('localizedFirstName'),
                'last_name': profile.get('localizedLastName'),
                'email': email,
                'profile_url': f"https://www.linkedin.com/in/{profile.get('vanityName', '')}"
            }
        except Exception as e:
            print(f"❌ LinkedIn profile error: {str(e)}")
            return None


def calculate_career_consistency_index(candidate: Dict, linkedin_data: Optional[Dict] = None) -> Dict:
    """
    Calculate Career Consistency Index (CCI) based on resume data and optional LinkedIn verification
    
    Scoring Factors:
    1. Job tenure stability (40%) - Penalize frequent job hopping
    2. Career progression (25%) - Look for upward movement
    3. Skill consistency (20%) - Related roles vs random jumps
    4. LinkedIn verification (15%) - Profile matches resume
    
    Args:
        candidate: Candidate dict with work_history, skills, resume_text
        linkedin_data: Optional LinkedIn profile data for verification
    
    Returns:
        Dict with CCI score (0-100) and detailed breakdown
    """
    
    work_history = candidate.get('work_history', [])
    
    if not work_history:
        return {
            'cci_score': 50,  # Neutral score for freshers
            'tenure_score': 50,
            'progression_score': 50,
            'consistency_score': 50,
            'verification_score': 0,
            'flags': ['No work history provided'],
            'strengths': ['Fresh perspective'],
            'concerns': [],
            'is_verified': False
        }
    
    # 1. Tenure Stability Score (40%)
    tenure_score = _calculate_tenure_stability(work_history)
    
    # 2. Career Progression Score (25%)
    progression_score = _calculate_career_progression(work_history)
    
    # 3. Skill Consistency Score (20%)
    consistency_score = _calculate_skill_consistency(work_history, candidate.get('skills', []))
    
    # 4. LinkedIn Verification Score (15%)
    verification_score = 0
    is_verified = False
    if linkedin_data:
        verification_score, is_verified = _verify_with_linkedin(candidate, linkedin_data)
    
    # Calculate weighted CCI
    cci_score = (
        tenure_score * 0.40 +
        progression_score * 0.25 +
        consistency_score * 0.20 +
        verification_score * 0.15
    )
    
    # Identify flags and strengths
    flags = []
    strengths = []
    concerns = []
    
    if tenure_score < 50:
        flags.append('Frequent job changes')
        concerns.append('Average tenure less than 1 year')
    elif tenure_score > 80:
        strengths.append('Stable career with good tenure')
    
    if progression_score > 75:
        strengths.append('Clear career progression')
    elif progression_score < 40:
        concerns.append('Unclear career progression')
    
    if consistency_score < 50:
        flags.append('Inconsistent role types')
        concerns.append('Multiple unrelated job switches')
    elif consistency_score > 75:
        strengths.append('Consistent specialization')
    
    if is_verified:
        strengths.append('LinkedIn profile verified')
    elif linkedin_data is None:
        flags.append('LinkedIn not verified')
    
    return {
        'cci_score': round(cci_score, 1),
        'tenure_score': round(tenure_score, 1),
        'progression_score': round(progression_score, 1),
        'consistency_score': round(consistency_score, 1),
        'verification_score': round(verification_score, 1),
        'flags': flags,
        'strengths': strengths,
        'concerns': concerns,
        'is_verified': is_verified,
        'recommendation': _get_cci_recommendation(cci_score)
    }


def _calculate_tenure_stability(work_history: List[Dict]) -> float:
    """
    Calculate tenure stability score
    - Penalize jobs < 1 year
    - Reward 2-4 year tenures
    - Slightly penalize > 5 years at one place (may indicate stagnation)
    """
    if not work_history:
        return 50
    
    tenures = []
    for job in work_history:
        start_date = job.get('start_date')
        end_date = job.get('end_date', 'Present')
        
        if start_date:
            tenure_months = _calculate_tenure_months(start_date, end_date)
            tenures.append(tenure_months)
    
    if not tenures:
        return 50
    
    avg_tenure_months = sum(tenures) / len(tenures)
    
    # Scoring logic
    if avg_tenure_months < 6:
        return 20  # Very short tenure
    elif avg_tenure_months < 12:
        return 40  # Less than 1 year average
    elif avg_tenure_months < 18:
        return 60  # 1-1.5 years
    elif avg_tenure_months < 36:
        return 85  # 1.5-3 years (ideal)
    elif avg_tenure_months < 60:
        return 90  # 3-5 years (very stable)
    else:
        return 75  # > 5 years (may indicate less adaptability)


def _calculate_career_progression(work_history: List[Dict]) -> float:
    """
    Detect upward career movement
    - Look for seniority keywords (Junior -> Senior -> Lead -> Manager)
    - Check for increasing responsibility
    """
    if len(work_history) < 2:
        return 50  # Not enough data
    
    # Sort by date (most recent first)
    sorted_history = sorted(
        work_history,
        key=lambda x: x.get('start_date', ''),
        reverse=True
    )
    
    seniority_levels = {
        'intern': 1,
        'trainee': 1,
        'junior': 2,
        'associate': 2,
        'mid-level': 3,
        'intermediate': 3,
        'senior': 4,
        'lead': 5,
        'principal': 6,
        'staff': 6,
        'manager': 6,
        'director': 7,
        'vp': 8,
        'cto': 9,
        'ceo': 10
    }
    
    levels = []
    for job in reversed(sorted_history):  # Oldest to newest
        title = job.get('title', '').lower()
        level = 3  # Default mid-level
        
        for keyword, rank in seniority_levels.items():
            if keyword in title:
                level = rank
                break
        
        levels.append(level)
    
    if len(levels) < 2:
        return 50
    
    # Check for progression
    progression_count = sum(1 for i in range(1, len(levels)) if levels[i] > levels[i-1])
    stagnation_count = sum(1 for i in range(1, len(levels)) if levels[i] == levels[i-1])
    regression_count = sum(1 for i in range(1, len(levels)) if levels[i] < levels[i-1])
    
    # Calculate score
    total_transitions = len(levels) - 1
    if total_transitions == 0:
        return 50
    
    progression_ratio = progression_count / total_transitions
    
    if regression_count > progression_count:
        return 30  # More regressions than progressions
    elif progression_ratio > 0.6:
        return 95  # Strong progression
    elif progression_ratio > 0.4:
        return 75  # Good progression
    elif progression_ratio > 0.2:
        return 60  # Some progression
    else:
        return 45  # Mostly flat


def _calculate_skill_consistency(work_history: List[Dict], skills: List[str]) -> float:
    """
    Check if roles are related or random jumps between unrelated fields
    """
    if not work_history:
        return 50
    
    # Extract role keywords
    role_keywords = []
    for job in work_history:
        title = job.get('title', '').lower()
        role_keywords.extend(title.split())
    
    # Common role families
    role_families = {
        'developer': ['developer', 'programmer', 'software', 'engineer', 'coding', 'fullstack'],
        'data': ['data', 'analyst', 'scientist', 'analytics', 'bi', 'ml', 'ai'],
        'design': ['designer', 'ux', 'ui', 'creative', 'visual'],
        'management': ['manager', 'director', 'lead', 'head', 'vp'],
        'devops': ['devops', 'sre', 'infrastructure', 'cloud', 'platform'],
        'sales': ['sales', 'account', 'business development', 'customer'],
        'marketing': ['marketing', 'growth', 'content', 'brand'],
        'product': ['product', 'pm', 'owner']
    }
    
    # Detect family for each job
    job_families = []
    for job in work_history:
        title = job.get('title', '').lower()
        detected_family = None
        
        for family, keywords in role_families.items():
            if any(keyword in title for keyword in keywords):
                detected_family = family
                break
        
        if detected_family:
            job_families.append(detected_family)
    
    if not job_families:
        return 50
    
    # Calculate consistency
    most_common_family = max(set(job_families), key=job_families.count)
    consistency_ratio = job_families.count(most_common_family) / len(job_families)
    
    # Score
    if consistency_ratio >= 0.8:
        return 90  # Very consistent
    elif consistency_ratio >= 0.6:
        return 75  # Mostly consistent
    elif consistency_ratio >= 0.4:
        return 55  # Some consistency
    else:
        return 35  # Very inconsistent


def _verify_with_linkedin(candidate: Dict, linkedin_data: Dict) -> Tuple[float, bool]:
    """
    Verify candidate information against LinkedIn profile
    Returns (verification_score, is_verified)
    """
    score = 0
    checks_passed = 0
    total_checks = 0
    
    # Check name match
    total_checks += 1
    candidate_name = candidate.get('name', '').lower()
    linkedin_name = f"{linkedin_data.get('first_name', '')} {linkedin_data.get('last_name', '')}".lower()
    
    if candidate_name and linkedin_name and candidate_name in linkedin_name:
        checks_passed += 1
    
    # Check email match
    total_checks += 1
    if candidate.get('email') == linkedin_data.get('email'):
        checks_passed += 1
    
    # Calculate score
    if total_checks > 0:
        score = (checks_passed / total_checks) * 100
    
    is_verified = score > 50
    
    return score, is_verified


def _calculate_tenure_months(start_date: str, end_date: str) -> int:
    """Calculate tenure in months between two dates"""
    try:
        # Parse dates (assuming YYYY-MM format)
        start = datetime.strptime(start_date[:7] if len(start_date) >= 7 else start_date, '%Y-%m')
        
        if end_date.lower() == 'present':
            end = datetime.now()
        else:
            end = datetime.strptime(end_date[:7] if len(end_date) >= 7 else end_date, '%Y-%m')
        
        months = (end.year - start.year) * 12 + (end.month - start.month)
        return max(1, months)  # At least 1 month
    except:
        return 12  # Default to 1 year if parsing fails


def _get_cci_recommendation(cci_score: float) -> str:
    """Get recommendation based on CCI score"""
    if cci_score >= 80:
        return "✅ Excellent career stability and progression. Strong hire."
    elif cci_score >= 65:
        return "👍 Good career consistency. Recommended for interview."
    elif cci_score >= 50:
        return "⚠️ Acceptable career path with some concerns. Discuss during interview."
    else:
        return "❌ Significant career inconsistencies. Requires thorough screening."


def calculate_social_proof_score(candidate: Dict, linkedin_profile: Optional[Dict] = None) -> Dict:
    """
    Calculate social proof score based on online presence
    
    Future enhancements:
    - GitHub contributions
    - Stack Overflow reputation
    - Published articles/blogs
    - Conference talks
    - Open source contributions
    
    Args:
        candidate: Candidate dictionary
        linkedin_profile: Optional LinkedIn profile data
    
    Returns:
        Social proof score and breakdown
    """
    score = 0
    factors = []
    
    # LinkedIn verification (40 points)
    if linkedin_profile and linkedin_profile.get('is_verified'):
        score += 40
        factors.append('LinkedIn profile verified')
    
    # GitHub presence (20 points) - placeholder for future
    github_url = candidate.get('github_url')
    if github_url:
        score += 20
        factors.append('GitHub profile provided')
    
    # Portfolio/Website (15 points)
    portfolio_url = candidate.get('portfolio_url')
    if portfolio_url:
        score += 15
        factors.append('Portfolio website provided')
    
    # Professional certifications (25 points)
    certifications = candidate.get('certifications', [])
    if certifications:
        cert_score = min(len(certifications) * 5, 25)
        score += cert_score
        factors.append(f'{len(certifications)} professional certifications')
    
    return {
        'social_proof_score': score,
        'max_score': 100,
        'factors': factors,
        'recommendation': 'Strong online presence' if score >= 60 else 
                         'Moderate online presence' if score >= 30 else
                         'Limited online presence'
    }


# ============================================================================
# FRESHER-SPECIFIC SCORING
# ============================================================================

def calculate_fresher_potential_score(candidate: Dict) -> Dict:
    """
    Alternative scoring for freshers/entry-level candidates
    Focuses on education, projects, internships, and potential rather than experience
    
    Scoring Factors:
    1. Education Quality (30%) - GPA, institution, relevant coursework
    2. Projects & Portfolio (30%) - Personal projects, GitHub, hackathons
    3. Internships (20%) - Relevant work experience
    4. Skills & Certifications (15%) - Technical skills, online courses
    5. Extracurricular (5%) - Leadership, clubs, volunteering
    
    Args:
        candidate: Candidate dictionary
    
    Returns:
        Potential score (0-100) and breakdown
    """
    
    # 1. Education Quality (30%)
    education_score = _score_education_quality(candidate.get('education', []))
    
    # 2. Projects & Portfolio (30%)
    projects_score = _score_projects_portfolio(candidate.get('projects', []), candidate)
    
    # 3. Internships (20%)
    internship_score = _score_internships(candidate.get('work_history', []))
    
    # 4. Skills & Certifications (15%)
    skills_score = _score_skills_certifications(
        candidate.get('skills', []),
        candidate.get('certifications', [])
    )
    
    # 5. Extracurricular (5%)
    extra_score = _score_extracurricular(candidate)
    
    # Calculate weighted potential score
    potential_score = (
        education_score * 0.30 +
        projects_score * 0.30 +
        internship_score * 0.20 +
        skills_score * 0.15 +
        extra_score * 0.05
    )
    
    # Identify strengths
    strengths = []
    areas_for_growth = []
    
    if education_score > 75:
        strengths.append('Strong academic background')
    elif education_score < 40:
        areas_for_growth.append('Academic performance')
    
    if projects_score > 70:
        strengths.append('Impressive project portfolio')
    elif projects_score < 40:
        areas_for_growth.append('Build more projects')
    
    if internship_score > 60:
        strengths.append('Relevant internship experience')
    elif internship_score < 30:
        areas_for_growth.append('Gain more practical experience')
    
    if skills_score > 70:
        strengths.append('Well-developed skill set')
    
    return {
        'potential_score': round(potential_score, 1),
        'education_score': round(education_score, 1),
        'projects_score': round(projects_score, 1),
        'internship_score': round(internship_score, 1),
        'skills_score': round(skills_score, 1),
        'extracurricular_score': round(extra_score, 1),
        'strengths': strengths,
        'areas_for_growth': areas_for_growth,
        'recommendation': _get_fresher_recommendation(potential_score),
        'is_fresher': True
    }


def _score_education_quality(education: List[Dict]) -> float:
    """Score education quality for freshers"""
    if not education:
        return 20
    
    score = 0
    
    for edu in education:
        # Check degree level
        degree = edu.get('degree', '').lower()
        if 'phd' in degree or 'doctorate' in degree:
            score += 40
        elif 'master' in degree or 'msc' in degree or 'mba' in degree:
            score += 35
        elif 'bachelor' in degree or 'bsc' in degree or 'btech' in degree or 'be ' in degree:
            score += 30
        elif 'associate' in degree or 'diploma' in degree:
            score += 20
        
        # Check GPA/grades
        gpa = edu.get('gpa', 0)
        if gpa >= 3.7:
            score += 30
        elif gpa >= 3.3:
            score += 20
        elif gpa >= 3.0:
            score += 10
        
        # Check institution reputation (basic keyword check)
        institution = edu.get('institution', '').lower()
        prestigious_keywords = ['iit', 'nit', 'stanford', 'mit', 'harvard', 'berkeley', 'carnegie']
        if any(keyword in institution for keyword in prestigious_keywords):
            score += 20
    
    return min(score, 100)


def _score_projects_portfolio(projects: List[Dict], candidate: Dict) -> float:
    """Score projects and portfolio quality"""
    score = 0
    
    # Number of projects
    num_projects = len(projects)
    if num_projects >= 5:
        score += 30
    elif num_projects >= 3:
        score += 20
    elif num_projects >= 1:
        score += 10
    
    # GitHub presence
    if candidate.get('github_url'):
        score += 25
    
    # Portfolio website
    if candidate.get('portfolio_url'):
        score += 20
    
    # Project complexity (check descriptions for keywords)
    complex_keywords = ['deployed', 'production', 'scale', 'users', 'database', 'api', 'ml', 'ai']
    for project in projects:
        desc = project.get('description', '').lower()
        if any(keyword in desc for keyword in complex_keywords):
            score += 5  # Up to 25 points for complex projects
    
    return min(score, 100)


def _score_internships(work_history: List[Dict]) -> float:
    """Score internship experience"""
    if not work_history:
        return 0
    
    internships = [job for job in work_history if 'intern' in job.get('title', '').lower()]
    
    if not internships:
        return 0
    
    score = 0
    
    # Number of internships
    score += min(len(internships) * 25, 50)
    
    # Duration
    for internship in internships:
        months = _calculate_tenure_months(
            internship.get('start_date', ''),
            internship.get('end_date', 'Present')
        )
        if months >= 6:
            score += 25
        elif months >= 3:
            score += 15
        else:
            score += 5
    
    return min(score, 100)


def _score_skills_certifications(skills: List[str], certifications: List[Dict]) -> float:
    """Score skills and certifications"""
    score = 0
    
    # Number of skills
    num_skills = len(skills)
    if num_skills >= 10:
        score += 40
    elif num_skills >= 5:
        score += 25
    elif num_skills >= 3:
        score += 15
    
    # Certifications
    score += min(len(certifications) * 15, 60)
    
    return min(score, 100)


def _score_extracurricular(candidate: Dict) -> float:
    """Score extracurricular activities"""
    score = 0
    
    # Leadership positions
    leadership_keywords = ['president', 'lead', 'captain', 'head', 'coordinator']
    resume_text = candidate.get('resume_text', '').lower()
    
    if any(keyword in resume_text for keyword in leadership_keywords):
        score += 50
    
    # Volunteering
    if 'volunteer' in resume_text or 'ngo' in resume_text:
        score += 30
    
    # Awards
    if 'award' in resume_text or 'prize' in resume_text or 'winner' in resume_text:
        score += 20
    
    return min(score, 100)


def _get_fresher_recommendation(score: float) -> str:
    """Get recommendation for fresher candidates"""
    if score >= 75:
        return "🌟 Exceptional potential! Highly recommended for hire."
    elif score >= 60:
        return "✅ Strong potential. Recommended for interview."
    elif score >= 45:
        return "👍 Good potential with room to grow."
    else:
        return "⚠️ Limited demonstrated potential. Consider with caution."
