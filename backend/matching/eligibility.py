"""
Eligibility logic for candidate pre-screening based on job requirements.
"""

def pre_eligibility_check(candidate, job):
    exp = candidate.get('experience_years', 0)
    job_type = job.get('experience_requirement_type', 'BOTH_ALLOWED')
    min_exp = job.get('min_experience_years', 0)
    max_exp = job.get('max_experience_years', 100)
    if job_type == 'FRESHER_ONLY':
        if exp > max_exp:
            return False, "Overqualified for fresher role"
    elif job_type == 'EXPERIENCE_REQUIRED':
        if exp < min_exp:
            return False, "Insufficient experience for this role"
    return True, "Eligible"
