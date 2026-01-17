"""
P0 ML: Fairness Audit Service
==============================
Bias detection and fairness evaluation for hiring decisions

Features:
- Demographic parity analysis
- Disparate impact calculation
- Equal opportunity metrics
- Fairness report generation
- Compatible with AIF360 methodology

Author: Smart Hiring System Team
Date: January 2026
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# P0 FIX: Make numpy optional for Lite environments
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    class MockNumpy:
        @staticmethod
        def array(data): return data
        @staticmethod
        def unique(data): return list(set(data))
        @staticmethod
        def mean(data): 
            if not data: return 0
            return sum(data) / len(data)
        @staticmethod
        def sum(data): return 0 # Simplified mock
    np = MockNumpy()

logger = logging.getLogger(__name__)

# Try to import fairlearn
FAIRLEARN_AVAILABLE = False
try:
    if NUMPY_AVAILABLE:
        from fairlearn.metrics import (
            demographic_parity_difference,
            demographic_parity_ratio,
            equalized_odds_difference,
        )
        FAIRLEARN_AVAILABLE = True
        logger.info("✅ Fairlearn available for bias detection")
    else:
        raise ImportError("Numpy missing")
except ImportError:
    logger.warning("⚠️ Fairlearn not installed - using custom fairness metrics")


class FairnessMetricsCalculator:
    """
    Calculate fairness metrics for hiring decisions
    
    Implements standard fairness metrics without requiring external libraries
    """
    
    def __init__(self, predictions: np.ndarray, labels: np.ndarray, 
                 sensitive_features: np.ndarray, favorable_label: int = 1):
        """
        Initialize fairness calculator
        """
        if not NUMPY_AVAILABLE:
            self.predictions = []
            self.labels = []
            self.sensitive_features = []
            self.groups = []
            return

        self.predictions = np.array(predictions)
        self.sensitive_features = np.array(sensitive_features)
        self.labels = np.array(labels) if labels is not None else None
        self.favorable_label = favorable_label
        
        self.groups = np.unique(self.sensitive_features)
        self._compute_group_stats()
        
    def _compute_group_stats(self):
        """Precompute statistics for each group"""
        self.group_stats = {}
        
        if not NUMPY_AVAILABLE:
            return

        for group in self.groups:
            mask = self.sensitive_features == group
            group_preds = self.predictions[mask]
            
            n = len(group_preds)
            n_positive = np.sum(group_preds == self.favorable_label)
            selection_rate = n_positive / n if n > 0 else 0
            
            stats = {
                'n': n,
                'n_positive': n_positive,
                'selection_rate': selection_rate
            }
            
            # If we have ground truth labels
            if self.labels is not None:
                group_labels = self.labels[mask]
                n_positive_label = np.sum(group_labels == self.favorable_label)
                
                # True Positive Rate (TPR)
                tp = np.sum((group_preds == self.favorable_label) & 
                           (group_labels == self.favorable_label))
                tpr = tp / n_positive_label if n_positive_label > 0 else 0
                
                # False Positive Rate (FPR)
                n_negative_label = n - n_positive_label
                fp = np.sum((group_preds == self.favorable_label) & 
                           (group_labels != self.favorable_label))
                fpr = fp / n_negative_label if n_negative_label > 0 else 0
                
                stats['tpr'] = tpr
                stats['fpr'] = fpr
                stats['n_positive_label'] = n_positive_label
            
            self.group_stats[str(group)] = stats
    
    def demographic_parity_difference(self) -> float:
        """
        Calculate Statistical Parity Difference
        """
        if not hasattr(self, 'group_stats') or not self.group_stats:
            return 0.0
        rates = [s['selection_rate'] for s in self.group_stats.values()]
        return float(max(rates) - min(rates)) if rates else 0.0
    
    def demographic_parity_ratio(self) -> float:
        """
        Calculate Statistical Parity Ratio (Disparate Impact)
        """
        if not hasattr(self, 'group_stats') or not self.group_stats:
            return 1.0
        rates = [s['selection_rate'] for s in self.group_stats.values()]
        if not rates or max(rates) == 0:
            return 1.0
        return float(min(rates) / max(rates))
    
    def equal_opportunity_difference(self) -> Optional[float]:
        """
        Calculate Equal Opportunity Difference (TPR disparity)
        """
        if getattr(self, 'labels', None) is None or not hasattr(self, 'group_stats'):
            return None
        
        tprs = [s.get('tpr', 0) for s in self.group_stats.values()]
        return float(max(tprs) - min(tprs)) if tprs else 0.0
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all fairness metrics"""
        metrics = {
            'demographic_parity_difference': round(self.demographic_parity_difference(), 4),
            'demographic_parity_ratio': round(self.demographic_parity_ratio(), 4),
            'disparate_impact': round(self.demographic_parity_ratio(), 4),  # Alias
        }
        
        eod = self.equal_opportunity_difference()
        if eod is not None:
            metrics['equal_opportunity_difference'] = round(eod, 4)
        
        # Add group statistics
        metrics['group_statistics'] = getattr(self, 'group_stats', {})
        
        # Add interpretations
        metrics['interpretations'] = self._interpret_metrics(metrics)
        
        return metrics
    
    def _interpret_metrics(self, metrics: Dict) -> Dict[str, str]:
        """Generate human-readable interpretations"""
        interpretations = {}
        
        dpd = metrics['demographic_parity_difference']
        if dpd < 0.05:
            interpretations['demographic_parity'] = "✅ FAIR - Selection rates are nearly equal across groups"
        elif dpd < 0.1:
            interpretations['demographic_parity'] = "⚠️ CAUTION - Minor disparity in selection rates"
        else:
            interpretations['demographic_parity'] = "❌ CONCERN - Significant disparity in selection rates"
        
        dpr = metrics['demographic_parity_ratio']
        if dpr >= 0.8:
            interpretations['disparate_impact'] = "✅ FAIR - Passes 80% rule (no disparate impact)"
        elif dpr >= 0.6:
            interpretations['disparate_impact'] = "⚠️ CAUTION - May indicate disparate impact"
        else:
            interpretations['disparate_impact'] = "❌ CONCERN - Likely disparate impact present"
        
        return interpretations


class FairnessAuditService:
    """
    P0 ML: Comprehensive fairness audit service for hiring decisions
    """
    
    def __init__(self):
        self.use_fairlearn = FAIRLEARN_AVAILABLE
        logger.info(f"FairnessAuditService initialized (fairlearn={self.use_fairlearn})")
    
    def audit_decisions(
        self,
        decisions: List[int],
        sensitive_attribute: List[Any],
        ground_truth: Optional[List[int]] = None,
        attribute_name: str = "protected_group"
    ) -> Dict[str, Any]:
        """
        Audit hiring decisions for fairness
        """
        if len(decisions) != len(sensitive_attribute):
            raise ValueError("Decisions and sensitive_attribute must have same length")
        
        if not NUMPY_AVAILABLE:
             return {
                'attribute_analyzed': attribute_name,
                'error': 'Fairness audit requires numpy',
                'metrics': {},
                'assessment': {'status': 'UNKNOWN', 'message': 'Missing dependencies'}
            }

        predictions = np.array(decisions)
        sensitive = np.array(sensitive_attribute)
        labels = np.array(ground_truth) if ground_truth else None
        
        # Calculate metrics using our custom implementation
        calculator = FairnessMetricsCalculator(predictions, labels, sensitive)
        metrics = calculator.get_all_metrics()
        
        # Also use fairlearn if available (for validation)
        if self.use_fairlearn and len(np.unique(sensitive)) >= 2:
            try:
                fl_dpd = demographic_parity_difference(
                    y_true=predictions,  # Using predictions as "true" for parity calc
                    y_pred=predictions,
                    sensitive_features=sensitive
                )
                metrics['fairlearn_dpd'] = round(fl_dpd, 4)
            except Exception as e:
                logger.warning(f"Fairlearn calculation failed: {e}")
        
        # Generate overall assessment
        assessment = self._generate_assessment(metrics)
        
        return {
            'attribute_analyzed': attribute_name,
            'sample_size': len(decisions),
            'group_count': len(np.unique(sensitive)),
            'positive_rate': float(np.mean(predictions)),
            'metrics': metrics,
            'assessment': assessment,
            'audited_at': datetime.utcnow().isoformat(),
            'fairlearn_available': self.use_fairlearn
        }
    
    def _generate_assessment(self, metrics: Dict) -> Dict[str, Any]:
        """Generate overall fairness assessment"""
        issues = []
        recommendations = []
        
        dpd = metrics['demographic_parity_difference']
        dpr = metrics['demographic_parity_ratio']
        
        # Check demographic parity
        if dpd > 0.1:
            issues.append({
                'type': 'demographic_parity',
                'severity': 'HIGH',
                'description': f'Selection rate difference of {dpd:.1%} exceeds 10% threshold'
            })
            recommendations.append('Review selection criteria for potential bias')
        
        # Check disparate impact (80% rule)
        if dpr < 0.8:
            issues.append({
                'type': 'disparate_impact',
                'severity': 'HIGH',
                'description': f'Disparate impact ratio of {dpr:.1%} is below 80% threshold'
            })
            recommendations.append('Investigate root cause of disparate impact')
            recommendations.append('Consider bias mitigation strategies')
        
        # Overall status
        if not issues:
            status = 'FAIR'
            status_message = 'No significant fairness issues detected'
        elif any(i['severity'] == 'HIGH' for i in issues):
            status = 'CONCERN'
            status_message = 'Significant fairness issues require attention'
        else:
            status = 'CAUTION'
            status_message = 'Minor fairness issues detected'
        
        return {
            'status': status,
            'status_message': status_message,
            'issues_count': len(issues),
            'issues': issues,
            'recommendations': recommendations
        }
    
    def audit_application_batch(
        self,
        applications: List[Dict],
        decision_field: str = 'decision',
        attribute_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Audit a batch of job applications for fairness
        
        Args:
            applications: List of application dicts
            decision_field: Field name containing the decision
            attribute_fields: List of sensitive attribute fields to analyze
            
        Returns:
            Dict with audit results for each attribute
        """
        if not applications:
            return {'error': 'No applications provided'}
        
        attribute_fields = attribute_fields or ['gender', 'age_group', 'ethnicity']
        
        # Extract decisions
        decisions = [1 if app.get(decision_field) in ['Hire', 'shortlisted', 1, True] else 0 
                    for app in applications]
        
        results = {
            'total_applications': len(applications),
            'positive_decisions': sum(decisions),
            'positive_rate': sum(decisions) / len(decisions) if decisions else 0,
            'audits_by_attribute': {},
            'audited_at': datetime.utcnow().isoformat()
        }
        
        # Audit each sensitive attribute
        for attr in attribute_fields:
            attr_values = [app.get(attr, 'unknown') for app in applications]
            
            # Skip if all values are the same or unknown
            unique_values = set(v for v in attr_values if v != 'unknown')
            if len(unique_values) < 2:
                results['audits_by_attribute'][attr] = {
                    'skipped': True,
                    'reason': 'Insufficient group diversity'
                }
                continue
            
            try:
                audit_result = self.audit_decisions(decisions, attr_values, attribute_name=attr)
                results['audits_by_attribute'][attr] = audit_result
            except Exception as e:
                results['audits_by_attribute'][attr] = {
                    'error': str(e)
                }
        
        # Generate overall summary
        has_concerns = any(
            r.get('assessment', {}).get('status') == 'CONCERN'
            for r in results['audits_by_attribute'].values()
            if isinstance(r, dict) and 'assessment' in r
        )
        
        results['overall_status'] = 'CONCERN' if has_concerns else 'FAIR'
        
        return results


# Singleton instance
_fairness_service = None

def get_fairness_service() -> FairnessAuditService:
    """Get or create fairness audit service singleton"""
    global _fairness_service
    if _fairness_service is None:
        _fairness_service = FairnessAuditService()
    return _fairness_service


if __name__ == '__main__':
    # Test the fairness service
    print("\n" + "="*60)
    print("🧪 FAIRNESS AUDIT SERVICE TEST")
    print("="*60 + "\n")
    
    service = get_fairness_service()
    
    # Simulate hiring decisions
    decisions = [1, 1, 1, 0, 0, 1, 0, 0, 1, 1,  # Group A: 60% positive
                 1, 0, 0, 0, 0, 1, 0, 0, 0, 0]  # Group B: 20% positive - bias!
    
    groups = ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A',
              'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B']
    
    result = service.audit_decisions(decisions, groups, attribute_name='group')
    
    print(f"Sample Size: {result.get('sample_size', 'N/A')}")
    print(f"Groups: {result.get('group_count', 'N/A')}")
    print(f"Overall Positive Rate: {result.get('positive_rate', 0):.1%}")
    print()
    if 'metrics' in result:
        print("📊 Fairness Metrics:")
        print(f"  - Demographic Parity Difference: {result['metrics']['demographic_parity_difference']}")
        print(f"  - Disparate Impact Ratio: {result['metrics']['disparate_impact']}")
        print()
        print("📋 Assessment:")
        print(f"  Status: {result['assessment']['status']}")
        print(f"  Message: {result['assessment']['status_message']}")
        print(f"  Issues: {result['assessment']['issues_count']}")
        for issue in result['assessment']['issues']:
            print(f"    - [{issue['severity']}] {issue['description']}")
        print()
        print("💡 Recommendations:")
        for rec in result['assessment']['recommendations']:
            print(f"  - {rec}")
    else:
        print(f"Error: {result.get('error')}")
    
    print("\n" + "="*60)
