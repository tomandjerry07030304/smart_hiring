"""
Explainability layer for candidate scoring.
"""

def generate_explanation(scores, decision, job_level, reason):
    explanation = scores.copy()
    explanation['decision'] = decision
    explanation['reasoning'] = reason
    explanation['job_level'] = job_level
    return explanation
