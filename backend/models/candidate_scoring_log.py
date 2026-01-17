from datetime import datetime

class CandidateScoringLog:
    """Log for candidate scoring and explainability."""
    collection_name = 'candidate_scoring_log'

    def __init__(self, candidate_id, job_id, scores, decision, explanation, timestamp=None):
        self.candidate_id = candidate_id
        self.job_id = job_id
        self.scores = scores  # dict of all sub-scores
        self.decision = decision
        self.explanation = explanation  # explainability dict
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self):
        return {
            'candidate_id': self.candidate_id,
            'job_id': self.job_id,
            'scores': self.scores,
            'decision': self.decision,
            'explanation': self.explanation,
            'timestamp': self.timestamp
        }
