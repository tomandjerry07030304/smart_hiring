"""
Decision engine for dynamic thresholds based on job level.
"""

THRESHOLDS = {
    'FRESHER': {'HIRE': 65, 'REVIEW': 50},
    'ENTRY': {'HIRE': 70, 'REVIEW': 55},
    'MID': {'HIRE': 75, 'REVIEW': 60},
    'SENIOR': {'HIRE': 80, 'REVIEW': 65}
}

def make_decision(final_score, job_level):
    t = THRESHOLDS.get(job_level.upper(), THRESHOLDS['ENTRY'])
    if final_score >= t['HIRE']:
        return 'HIRE'
    elif final_score >= t['REVIEW']:
        return 'REVIEW'
    else:
        return 'REJECT'
