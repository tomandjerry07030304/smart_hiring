from datetime import datetime

class FairnessAudit:
    """Fairness audit report model"""
    
    collection_name = 'fairness_audits'
    
    def __init__(self, job_id, **kwargs):
        self.job_id = job_id
        self.audit_date = kwargs.get('audit_date', datetime.utcnow())
        self.total_applications = kwargs.get('total_applications', 0)
        self.demographic_data = kwargs.get('demographic_data', {})
        
        # Fairness metrics
        self.demographic_parity = kwargs.get('demographic_parity', {})
        self.equal_opportunity = kwargs.get('equal_opportunity', {})
        self.disparate_impact = kwargs.get('disparate_impact', {})
        
        # Selection rates by group
        self.selection_rates = kwargs.get('selection_rates', {})
        
        # Bias indicators
        self.bias_detected = kwargs.get('bias_detected', False)
        self.bias_groups = kwargs.get('bias_groups', [])
        self.recommendations = kwargs.get('recommendations', [])
        
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        
    def to_dict(self):
        return {
            'job_id': self.job_id,
            'audit_date': self.audit_date,
            'total_applications': self.total_applications,
            'demographic_data': self.demographic_data,
            'demographic_parity': self.demographic_parity,
            'equal_opportunity': self.equal_opportunity,
            'disparate_impact': self.disparate_impact,
            'selection_rates': self.selection_rates,
            'bias_detected': self.bias_detected,
            'bias_groups': self.bias_groups,
            'recommendations': self.recommendations,
            'created_at': self.created_at
        }

class TransparencyReport:
    """Algorithmic transparency report for candidates"""
    
    collection_name = 'transparency_reports'
    
    def __init__(self, application_id, candidate_id, job_id, **kwargs):
        self.application_id = application_id
        self.candidate_id = candidate_id
        self.job_id = job_id
        
        # Scoring breakdown
        self.resume_score = kwargs.get('resume_score', 0.0)
        self.skill_score = kwargs.get('skill_score', 0.0)
        self.cci_score = kwargs.get('cci_score', 0.0)
        self.assessment_score = kwargs.get('assessment_score', 0.0)
        self.overall_score = kwargs.get('overall_score', 0.0)
        
        # Factors
        self.positive_factors = kwargs.get('positive_factors', [])
        self.negative_factors = kwargs.get('negative_factors', [])
        self.matched_skills = kwargs.get('matched_skills', [])
        self.missing_skills = kwargs.get('missing_skills', [])
        
        # Decision explanation
        self.decision = kwargs.get('decision', '')
        self.decision_rationale = kwargs.get('decision_rationale', '')
        self.improvement_suggestions = kwargs.get('improvement_suggestions', [])
        
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        
    def to_dict(self):
        return {
            'application_id': self.application_id,
            'candidate_id': self.candidate_id,
            'job_id': self.job_id,
            'resume_score': self.resume_score,
            'skill_score': self.skill_score,
            'cci_score': self.cci_score,
            'assessment_score': self.assessment_score,
            'overall_score': self.overall_score,
            'positive_factors': self.positive_factors,
            'negative_factors': self.negative_factors,
            'matched_skills': self.matched_skills,
            'missing_skills': self.missing_skills,
            'decision': self.decision,
            'decision_rationale': self.decision_rationale,
            'improvement_suggestions': self.improvement_suggestions,
            'created_at': self.created_at
        }
