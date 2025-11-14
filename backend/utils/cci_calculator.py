from datetime import datetime
import re

def calculate_career_consistency_index(experience_list):
    """
    Calculate Career Consistency Index (CCI) based on job history
    
    CCI measures job stability and career progression
    Factors:
    - Job tenure (longer is better)
    - Number of job changes
    - Career progression (promotions, title changes)
    - Gap periods between jobs
    
    Args:
        experience_list: List of dicts with {company, title, start_date, end_date}
    
    Returns:
        float: CCI score (0-100)
    """
    if not experience_list or len(experience_list) == 0:
        return 50.0  # Neutral score for no experience
    
    total_score = 0
    factors = []
    
    # Factor 1: Average job tenure (40 points)
    tenure_score = calculate_tenure_score(experience_list)
    factors.append(('tenure', tenure_score))
    
    # Factor 2: Job change frequency (30 points)
    frequency_score = calculate_frequency_score(experience_list)
    factors.append(('frequency', frequency_score))
    
    # Factor 3: Career progression (20 points)
    progression_score = calculate_progression_score(experience_list)
    factors.append(('progression', progression_score))
    
    # Factor 4: Employment gaps (10 points)
    gap_score = calculate_gap_score(experience_list)
    factors.append(('gaps', gap_score))
    
    # Total CCI
    cci = tenure_score * 0.4 + frequency_score * 0.3 + progression_score * 0.2 + gap_score * 0.1
    
    return {
        'cci_score': round(cci, 2),
        'factor_breakdown': {k: round(v, 2) for k, v in factors},
        'interpretation': interpret_cci(cci)
    }

def calculate_tenure_score(experience_list):
    """Calculate score based on job tenure"""
    tenures = []
    
    for exp in experience_list:
        start = exp.get('start_date')
        end = exp.get('end_date') or datetime.now()
        
        if isinstance(start, str):
            start = parse_date(start)
        if isinstance(end, str):
            end = parse_date(end)
        
        if start and end:
            tenure_years = (end - start).days / 365.25
            tenures.append(tenure_years)
    
    if not tenures:
        return 50.0
    
    avg_tenure = sum(tenures) / len(tenures)
    
    # Scoring: 2+ years = 100, 1 year = 70, 6 months = 40, <6 months = 20
    if avg_tenure >= 2:
        return 100.0
    elif avg_tenure >= 1:
        return 70.0 + (avg_tenure - 1) * 30
    elif avg_tenure >= 0.5:
        return 40.0 + (avg_tenure - 0.5) * 60
    else:
        return max(20.0, avg_tenure * 40)

def calculate_frequency_score(experience_list):
    """Calculate score based on job change frequency"""
    num_jobs = len(experience_list)
    
    # Get total career span
    all_dates = []
    for exp in experience_list:
        start = exp.get('start_date')
        if isinstance(start, str):
            start = parse_date(start)
        if start:
            all_dates.append(start)
    
    if not all_dates:
        return 50.0
    
    career_span_years = (datetime.now() - min(all_dates)).days / 365.25
    
    if career_span_years < 1:
        return 80.0  # Early career, don't penalize
    
    jobs_per_year = num_jobs / career_span_years
    
    # Scoring: <0.5 jobs/year = 100, 0.5-1 = 70, 1-2 = 40, >2 = 20
    if jobs_per_year < 0.5:
        return 100.0
    elif jobs_per_year < 1:
        return 70.0
    elif jobs_per_year < 2:
        return 40.0
    else:
        return max(20.0, 40 - (jobs_per_year - 2) * 10)

def calculate_progression_score(experience_list):
    """Calculate score based on career progression"""
    if len(experience_list) < 2:
        return 60.0  # Neutral for single job
    
    # Look for progression keywords in titles
    progression_keywords = {
        'junior': 1,
        'associate': 2,
        'senior': 4,
        'lead': 5,
        'principal': 6,
        'manager': 5,
        'director': 7,
        'vp': 8,
        'head': 7,
        'chief': 9
    }
    
    levels = []
    for exp in experience_list:
        title = exp.get('title', '').lower()
        level = 3  # Default mid-level
        for keyword, value in progression_keywords.items():
            if keyword in title:
                level = value
                break
        levels.append(level)
    
    # Check if levels are generally increasing
    if len(levels) < 2:
        return 60.0
    
    increases = sum(1 for i in range(1, len(levels)) if levels[i] > levels[i-1])
    progression_rate = increases / (len(levels) - 1)
    
    # Score based on progression rate
    if progression_rate >= 0.5:
        return 100.0
    elif progression_rate >= 0.3:
        return 80.0
    elif progression_rate >= 0.1:
        return 60.0
    else:
        return 40.0

def calculate_gap_score(experience_list):
    """Calculate score based on employment gaps"""
    if len(experience_list) < 2:
        return 100.0  # No gaps possible
    
    # Sort by start date
    sorted_exp = sorted(experience_list, key=lambda x: parse_date(x.get('start_date')))
    
    gaps_months = []
    for i in range(1, len(sorted_exp)):
        prev_end = sorted_exp[i-1].get('end_date')
        curr_start = sorted_exp[i].get('start_date')
        
        if isinstance(prev_end, str):
            prev_end = parse_date(prev_end)
        if isinstance(curr_start, str):
            curr_start = parse_date(curr_start)
        
        if prev_end and curr_start:
            gap_days = (curr_start - prev_end).days
            if gap_days > 30:  # More than 1 month
                gaps_months.append(gap_days / 30)
    
    if not gaps_months:
        return 100.0
    
    total_gap_months = sum(gaps_months)
    
    # Scoring: 0 gaps = 100, <3 months = 90, 3-6 = 70, 6-12 = 50, >12 = 30
    if total_gap_months == 0:
        return 100.0
    elif total_gap_months < 3:
        return 90.0
    elif total_gap_months < 6:
        return 70.0
    elif total_gap_months < 12:
        return 50.0
    else:
        return max(30.0, 50 - (total_gap_months - 12) * 2)

def parse_date(date_str):
    """Parse date from string"""
    if isinstance(date_str, datetime):
        return date_str
    
    if not date_str or date_str.lower() in ['present', 'current', 'now']:
        return datetime.now()
    
    # Try common formats
    formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%B %Y',
        '%b %Y',
        '%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    
    return None

def interpret_cci(score):
    """Interpret CCI score"""
    if score >= 80:
        return "Excellent - Very stable career progression"
    elif score >= 70:
        return "Good - Stable with consistent growth"
    elif score >= 60:
        return "Average - Moderate stability"
    elif score >= 50:
        return "Fair - Some instability concerns"
    else:
        return "Poor - Significant instability"
