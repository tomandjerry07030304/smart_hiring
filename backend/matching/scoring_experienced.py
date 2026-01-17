"""
Scoring logic for mid/senior jobs: Strong experience and domain weighting.
"""

def score_experienced(candidate, job):
    skill_score = candidate.get('skill_score', 0)
    experience_score = candidate.get('experience_score', 0)
    domain_score = candidate.get('domain_score', 0)
    certification_score = candidate.get('certification_score', 0)
    final_score = 0.4 * skill_score + 0.4 * experience_score + 0.1 * domain_score + 0.1 * certification_score
    return {
        'skill_score': skill_score,
        'experience_score': experience_score,
        'domain_score': domain_score,
        'certification_score': certification_score,
        'final_score': round(final_score, 2)
    }
