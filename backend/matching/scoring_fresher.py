"""
Scoring logic for fresher jobs: No experience penalty, focus on skills, projects, certifications.
"""

def score_fresher(candidate, job):
    skill_score = candidate.get('skill_score', 0)
    project_score = candidate.get('project_score', 0)
    certification_score = candidate.get('certification_score', 0)
    final_score = 0.6 * skill_score + 0.25 * project_score + 0.15 * certification_score
    return {
        'skill_score': skill_score,
        'project_score': project_score,
        'certification_score': certification_score,
        'experience_score': 0,
        'final_score': round(final_score, 2)
    }
