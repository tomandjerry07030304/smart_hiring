"""
Scoring logic for entry-level jobs: Partial experience weighting.
"""

def score_entry(candidate, job):
    skill_score = candidate.get('skill_score', 0)
    project_score = candidate.get('project_score', 0)
    certification_score = candidate.get('certification_score', 0)
    exp = candidate.get('experience_years', 0)
    max_exp = job.get('max_experience_years', 2)
    experience_score = min(exp / max_exp, 1.0) * 100 if max_exp > 0 else 0
    final_score = 0.5 * skill_score + 0.25 * experience_score + 0.15 * project_score + 0.1 * certification_score
    return {
        'skill_score': skill_score,
        'experience_score': round(experience_score, 2),
        'project_score': project_score,
        'certification_score': certification_score,
        'final_score': round(final_score, 2)
    }
