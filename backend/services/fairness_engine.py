"""
Custom Lightweight Fairness Evaluation Engine
==================================================
Replaces AIF360 for Render deployment compatibility

This module implements fairness metrics from scratch using only numpy, pandas, and scikit-learn.
Designed specifically for deployment environments with limited system dependencies.

Mathematical Background:
------------------------
1. **Demographic Parity (Statistical Parity)**
   - Definition: P(Ŷ=1|A=0) = P(Ŷ=1|A=1)
   - Measures: Whether positive prediction rates are equal across groups
   - Threshold: Difference < 0.1 (10%) indicates fairness

2. **Disparate Impact**
   - Definition: P(Ŷ=1|A=0) / P(Ŷ=1|A=1)
   - Measures: Ratio of selection rates between groups
   - 80% Rule: Ratio should be >= 0.8

3. **Equal Opportunity**
   - Definition: P(Ŷ=1|Y=1,A=0) = P(Ŷ=1|Y=1,A=1)
   - Measures: True positive rates across groups
   - Ensures qualified candidates have equal chances

4. **Equalized Odds**
   - Combines: Equal TPR and Equal FPR across groups
   - Ensures: Fair treatment for both positive and negative cases

5. **Predictive Parity**
   - Definition: P(Y=1|Ŷ=1,A=0) = P(Y=1|Ŷ=1,A=1)
   - Measures: Precision equality across groups

Author: Smart Hiring System Team
Date: December 2025
License: MIT
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FairnessMetrics:
    """
    Comprehensive fairness metrics calculator
    
    Implements all major fairness metrics without external fairness libraries.
    Uses only numpy and pandas for maximum compatibility.
    """
    
    def __init__(self, predictions: np.ndarray, labels: np.ndarray, 
                 sensitive_features: np.ndarray, favorable_label: int = 1):
        """
        Initialize fairness metrics calculator
        
        Args:
            predictions: Binary predictions (0 or 1)
            labels: Ground truth labels (0 or 1)
            sensitive_features: Protected attribute values (e.g., gender, race)
            favorable_label: Positive outcome value (default: 1)
        """
        self.predictions = np.array(predictions)
        self.labels = np.array(labels)
        self.sensitive_features = np.array(sensitive_features)
        self.favorable_label = favorable_label
        
        # Validate inputs
        if len(self.predictions) != len(self.labels) != len(self.sensitive_features):
            raise ValueError("All arrays must have the same length")
        
        self.groups = np.unique(self.sensitive_features)
        self._compute_group_statistics()
    
    def _compute_group_statistics(self):
        """Precompute statistics for each group"""
        self.group_stats = {}
        
        for group in self.groups:
            mask = self.sensitive_features == group
            group_preds = self.predictions[mask]
            group_labels = self.labels[mask]
            
            n = len(group_preds)
            n_positive_pred = np.sum(group_preds == self.favorable_label)
            n_positive_label = np.sum(group_labels == self.favorable_label)
            n_negative_label = np.sum(group_labels != self.favorable_label)
            
            # True Positives, False Positives, True Negatives, False Negatives
            tp = np.sum((group_preds == self.favorable_label) & (group_labels == self.favorable_label))
            fp = np.sum((group_preds == self.favorable_label) & (group_labels != self.favorable_label))
            tn = np.sum((group_preds != self.favorable_label) & (group_labels != self.favorable_label))
            fn = np.sum((group_preds != self.favorable_label) & (group_labels == self.favorable_label))
            
            # Rates
            selection_rate = n_positive_pred / n if n > 0 else 0
            base_rate = n_positive_label / n if n > 0 else 0
            
            tpr = tp / n_positive_label if n_positive_label > 0 else 0  # True Positive Rate
            fpr = fp / n_negative_label if n_negative_label > 0 else 0  # False Positive Rate
            tnr = tn / n_negative_label if n_negative_label > 0 else 0  # True Negative Rate
            fnr = fn / n_positive_label if n_positive_label > 0 else 0  # False Negative Rate
            
            precision = tp / n_positive_pred if n_positive_pred > 0 else 0
            recall = tpr
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            self.group_stats[str(group)] = {
                'n': n,
                'selection_rate': selection_rate,
                'base_rate': base_rate,
                'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn,
                'tpr': tpr, 'fpr': fpr, 'tnr': tnr, 'fnr': fnr,
                'precision': precision, 'recall': recall, 'f1': f1
            }
    
    def demographic_parity_difference(self) -> float:
        """
        Calculate Statistical Parity Difference (SPD)
        
        SPD = max(selection_rates) - min(selection_rates)
        
        Returns:
            float: Difference in selection rates (0 = perfect parity, >0.1 indicates bias)
        """
        selection_rates = [stats['selection_rate'] for stats in self.group_stats.values()]
        if not selection_rates:
            return 0.0
        return float(max(selection_rates) - min(selection_rates))
    
    def demographic_parity_ratio(self) -> float:
        """
        Calculate Statistical Parity Ratio
        
        Returns ratio of min to max selection rates
        
        Returns:
            float: Ratio (1.0 = perfect parity, <0.8 indicates bias)
        """
        selection_rates = [stats['selection_rate'] for stats in self.group_stats.values()]
        if not selection_rates or max(selection_rates) == 0:
            return 1.0
        return float(min(selection_rates) / max(selection_rates))
    
    def disparate_impact(self) -> Dict[str, float]:
        """
        Calculate Disparate Impact ratios for all group pairs
        
        Disparate Impact = Selection_Rate(Group_A) / Selection_Rate(Group_B)
        
        The 80% rule: DI should be >= 0.8
        
        Returns:
            dict: Pairwise disparate impact ratios
        """
        ratios = {}
        groups = list(self.groups)
        
        for i, group1 in enumerate(groups):
            for group2 in groups[i+1:]:
                rate1 = self.group_stats[str(group1)]['selection_rate']
                rate2 = self.group_stats[str(group2)]['selection_rate']
                
                if rate2 > 0:
                    ratio = rate1 / rate2
                    ratios[f"{group1}_vs_{group2}"] = round(ratio, 4)
                    
                    # Also compute reverse for symmetry
                    if rate1 > 0:
                        ratios[f"{group2}_vs_{group1}"] = round(rate2 / rate1, 4)
        
        return ratios
    
    def equal_opportunity_difference(self) -> float:
        """
        Calculate Equal Opportunity Difference
        
        EOD = |TPR(Group_A) - TPR(Group_B)|
        
        Measures if qualified individuals have equal chance of positive outcome
        
        Returns:
            float: Maximum TPR difference across groups
        """
        tprs = [stats['tpr'] for stats in self.group_stats.values()]
        if not tprs:
            return 0.0
        return float(max(tprs) - min(tprs))
    
    def average_odds_difference(self) -> float:
        """
        Calculate Average Odds Difference
        
        AOD = 0.5 * (|TPR_diff| + |FPR_diff|)
        
        Measures both TPR and FPR disparity
        
        Returns:
            float: Average of TPR and FPR differences
        """
        tprs = [stats['tpr'] for stats in self.group_stats.values()]
        fprs = [stats['fpr'] for stats in self.group_stats.values()]
        
        if not tprs or not fprs:
            return 0.0
        
        tpr_diff = max(tprs) - min(tprs)
        fpr_diff = max(fprs) - min(fprs)
        
        return float(0.5 * (tpr_diff + fpr_diff))

    # Alias: equalized_odds_difference delegates to average_odds_difference
    # (same metric, different naming convention used by Fairlearn vs AIF360)
    def equalized_odds_difference(self) -> float:
        """Alias for average_odds_difference (Fairlearn naming convention)."""
        return self.average_odds_difference()
    
    def predictive_parity_difference(self) -> float:
        """
        Calculate Predictive Parity Difference (Precision difference)
        
        PPD = |Precision(Group_A) - Precision(Group_B)|
        
        Returns:
            float: Maximum precision difference
        """
        precisions = [stats['precision'] for stats in self.group_stats.values()]
        if not precisions:
            return 0.0
        return float(max(precisions) - min(precisions))
    
    def false_positive_rate_difference(self) -> float:
        """
        Calculate False Positive Rate Difference
        
        FPR_diff = |FPR(Group_A) - FPR(Group_B)|
        
        Returns:
            float: Maximum FPR difference
        """
        fprs = [stats['fpr'] for stats in self.group_stats.values()]
        if not fprs:
            return 0.0
        return float(max(fprs) - min(fprs))
    
    def false_negative_rate_difference(self) -> float:
        """
        Calculate False Negative Rate Difference
        
        FNR_diff = |FNR(Group_A) - FNR(Group_B)|
        
        Returns:
            float: Maximum FNR difference
        """
        fnrs = [stats['fnr'] for stats in self.group_stats.values()]
        if not fnrs:
            return 0.0
        return float(max(fnrs) - min(fnrs))
    
    def theil_index(self) -> float:
        """
        Calculate Theil Index (generalized entropy index)
        
        Measures inequality in outcomes across groups
        
        Returns:
            float: Theil index (0 = perfect equality)
        """
        benefits = []
        for stats in self.group_stats.values():
            # Benefit = 1 for positive prediction, 0 for negative
            benefit = stats['tp'] + stats['fp']
            benefits.append(benefit)
        
        total_benefit = sum(benefits)
        if total_benefit == 0:
            return 0.0
        
        n_total = sum(stats['n'] for stats in self.group_stats.values())
        mu = total_benefit / n_total
        
        theil = 0.0
        for i, stats in enumerate(self.group_stats.values()):
            if benefits[i] > 0:
                theil += (benefits[i] / total_benefit) * np.log(benefits[i] / (stats['n'] * mu))
        
        return float(theil)
    
    def get_all_metrics(self) -> Dict[str, Union[float, Dict]]:
        """
        Calculate all fairness metrics
        
        Returns:
            dict: Complete set of fairness metrics
        """
        return {
            'demographic_parity_difference': round(self.demographic_parity_difference(), 4),
            'demographic_parity_ratio': round(self.demographic_parity_ratio(), 4),
            'disparate_impact': self.disparate_impact(),
            'equal_opportunity_difference': round(self.equal_opportunity_difference(), 4),
            'average_odds_difference': round(self.average_odds_difference(), 4),
            'predictive_parity_difference': round(self.predictive_parity_difference(), 4),
            'false_positive_rate_difference': round(self.false_positive_rate_difference(), 4),
            'false_negative_rate_difference': round(self.false_negative_rate_difference(), 4),
            'theil_index': round(self.theil_index(), 4)
        }
    
    def get_group_statistics(self) -> Dict[str, Dict]:
        """
        Get detailed statistics for each group
        
        Returns:
            dict: Statistics for each protected group
        """
        return {
            group: {
                'count': int(stats['n']),
                'selection_rate': round(stats['selection_rate'], 4),
                'true_positive_rate': round(stats['tpr'], 4),
                'false_positive_rate': round(stats['fpr'], 4),
                'precision': round(stats['precision'], 4),
                'recall': round(stats['recall'], 4),
                'f1_score': round(stats['f1'], 4)
            }
            for group, stats in self.group_stats.items()
        }

    # ── Convenience aliases used by fairness_proxy.py ─────────────────────────

    def group_fairness_metrics(self) -> Dict[str, Dict]:
        """Alias for get_group_statistics() — used by fairness_proxy."""
        return self.get_group_statistics()

    def overall_fairness_score(self) -> float:
        """
        Compute a single 0-100 fairness score from all metrics.

        Deductions are applied for each metric exceeding its threshold:
          demographic_parity_difference > 0.1  →  -20
          equal_opportunity_difference  > 0.1  →  -20
          average_odds_difference       > 0.1  →  -15
          predictive_parity_difference  > 0.15 →  -10
          disparate_impact ratio        < 0.8  →  -15
          theil_index                   > 0.15 →  -10

        Returns:
            float: Score between 0 and 100 (higher is fairer).
        """
        score = 100.0
        if self.demographic_parity_difference() > 0.1:
            score -= 20
        if self.equal_opportunity_difference() > 0.1:
            score -= 20
        if self.average_odds_difference() > 0.1:
            score -= 15
        if self.predictive_parity_difference() > 0.15:
            score -= 10
        # Disparate impact: check if any pairwise ratio < 0.8
        di = self.disparate_impact()
        if di and min(di.values()) < 0.8:
            score -= 15
        if self.theil_index() > 0.15:
            score -= 10
        return max(0.0, round(score, 2))

    def is_fair(self, dp_threshold: float = 0.1,
                di_threshold: float = 0.8,
                eo_threshold: float = 0.1) -> bool:
        """
        Quick boolean check — returns True if core metrics are within thresholds.

        Args:
            dp_threshold: Max demographic parity difference (default 0.1).
            di_threshold: Min disparate impact ratio (default 0.8 per 4/5 rule).
            eo_threshold: Max equal opportunity difference (default 0.1).
        """
        if self.demographic_parity_difference() > dp_threshold:
            return False
        if self.equal_opportunity_difference() > eo_threshold:
            return False
        di = self.disparate_impact()
        if di and min(di.values()) < di_threshold:
            return False
        return True


class BiasDetector:
    """
    High-level bias detection and reporting system
    """
    
    # Fairness thresholds based on research and legal standards
    THRESHOLDS = {
        'demographic_parity_difference': 0.1,  # 10% rule
        'demographic_parity_ratio': 0.8,  # 80% rule
        'disparate_impact': 0.8,  # 80% rule
        'equal_opportunity_difference': 0.1,
        'average_odds_difference': 0.1,
        'predictive_parity_difference': 0.1,
        'false_positive_rate_difference': 0.1,
        'false_negative_rate_difference': 0.1
    }
    
    @staticmethod
    def detect_bias(metrics: Dict[str, Union[float, Dict]]) -> Dict[str, any]:
        """
        Detect bias based on fairness metrics
        
        Args:
            metrics: Dictionary of fairness metrics
        
        Returns:
            dict: Bias detection results with severity and recommendations
        """
        bias_detected = False
        violations = []
        severity_score = 0
        
        # Check demographic parity
        if metrics['demographic_parity_difference'] > BiasDetector.THRESHOLDS['demographic_parity_difference']:
            violation_severity = 'high' if metrics['demographic_parity_difference'] > 0.2 else 'medium'
            violations.append({
                'metric': 'Demographic Parity',
                'value': metrics['demographic_parity_difference'],
                'threshold': BiasDetector.THRESHOLDS['demographic_parity_difference'],
                'severity': violation_severity,
                'description': f"Selection rates differ by {metrics['demographic_parity_difference']:.1%} across groups"
            })
            bias_detected = True
            severity_score += 3 if violation_severity == 'high' else 2
        
        # Check disparate impact (80% rule)
        if metrics['demographic_parity_ratio'] < BiasDetector.THRESHOLDS['demographic_parity_ratio']:
            violation_severity = 'high' if metrics['demographic_parity_ratio'] < 0.6 else 'medium'
            violations.append({
                'metric': 'Disparate Impact (80% Rule)',
                'value': metrics['demographic_parity_ratio'],
                'threshold': BiasDetector.THRESHOLDS['disparate_impact'],
                'severity': violation_severity,
                'description': f"Selection rate ratio is {metrics['demographic_parity_ratio']:.2f}, below the 80% threshold"
            })
            bias_detected = True
            severity_score += 4 if violation_severity == 'high' else 2
        
        # Check equal opportunity
        if metrics['equal_opportunity_difference'] > BiasDetector.THRESHOLDS['equal_opportunity_difference']:
            violations.append({
                'metric': 'Equal Opportunity',
                'value': metrics['equal_opportunity_difference'],
                'threshold': BiasDetector.THRESHOLDS['equal_opportunity_difference'],
                'severity': 'medium',
                'description': f"Qualified candidates have {metrics['equal_opportunity_difference']:.1%} difference in selection rates"
            })
            bias_detected = True
            severity_score += 2
        
        # Check equalized odds
        if metrics['average_odds_difference'] > BiasDetector.THRESHOLDS['average_odds_difference']:
            violations.append({
                'metric': 'Equalized Odds',
                'value': metrics['average_odds_difference'],
                'threshold': BiasDetector.THRESHOLDS['average_odds_difference'],
                'severity': 'medium',
                'description': f"Average difference in TPR and FPR is {metrics['average_odds_difference']:.1%}"
            })
            bias_detected = True
            severity_score += 2
        
        # Check FPR difference
        if metrics['false_positive_rate_difference'] > BiasDetector.THRESHOLDS['false_positive_rate_difference']:
            violations.append({
                'metric': 'False Positive Rate Parity',
                'value': metrics['false_positive_rate_difference'],
                'threshold': BiasDetector.THRESHOLDS['false_positive_rate_difference'],
                'severity': 'low',
                'description': f"False positive rates differ by {metrics['false_positive_rate_difference']:.1%}"
            })
            severity_score += 1
        
        # Determine overall severity
        if severity_score >= 6:
            overall_severity = 'critical'
        elif severity_score >= 4:
            overall_severity = 'high'
        elif severity_score >= 2:
            overall_severity = 'medium'
        else:
            overall_severity = 'low'
        
        return {
            'bias_detected': bias_detected,
            'overall_severity': overall_severity,
            'severity_score': severity_score,
            'violations': violations,
            'total_violations': len(violations)
        }
    
    @staticmethod
    def generate_recommendations(violations: List[Dict]) -> List[str]:
        """
        Generate actionable recommendations based on violations
        
        Args:
            violations: List of fairness violations
        
        Returns:
            list: Actionable recommendations
        """
        recommendations = []
        
        has_demographic_parity_issue = any(v['metric'] == 'Demographic Parity' for v in violations)
        has_disparate_impact = any(v['metric'] == 'Disparate Impact (80% Rule)' for v in violations)
        has_equal_opportunity_issue = any(v['metric'] == 'Equal Opportunity' for v in violations)
        
        if has_demographic_parity_issue or has_disparate_impact:
            recommendations.extend([
                "🔍 Implement blind resume screening to remove demographic identifiers",
                "📊 Review and adjust selection criteria to ensure group-neutrality",
                "🎯 Set diversity hiring goals with measurable targets",
                "⚖️ Conduct regular audits using this fairness dashboard"
            ])
        
        if has_equal_opportunity_issue:
            recommendations.extend([
                "📝 Use structured interviews with standardized questions",
                "👥 Diversify interview panels to reduce unconscious bias",
                "🎓 Provide unconscious bias training for all hiring personnel",
                "✅ Implement competency-based assessments rather than subjective evaluations"
            ])
        
        if len(violations) >= 3:
            recommendations.extend([
                "🚨 URGENT: Pause hiring process and conduct comprehensive bias audit",
                "🔧 Engage external consultant for bias mitigation strategy",
                "📚 Review and update all hiring policies and procedures",
                "💼 Consider implementing bias-mitigation technology"
            ])
        
        if not violations:
            recommendations = [
                "✅ Continue current fair hiring practices",
                "📈 Maintain regular monitoring of fairness metrics",
                "🎯 Share best practices with other teams",
                "🏆 Consider certification in fair hiring practices"
            ]
        
        return recommendations


def analyze_hiring_fairness_comprehensive(
    applications: pd.DataFrame,
    protected_attribute: str = 'gender',
    decision_column: str = 'decision',
    ground_truth_column: Optional[str] = 'ground_truth',
    favorable_label: int = 1
) -> Dict:
    """
    Comprehensive fairness analysis for hiring decisions
    
    This is the main entry point for fairness evaluation in the hiring system.
    
    Args:
        applications: DataFrame with application data
        protected_attribute: Column name for protected attribute (e.g., 'gender', 'ethnicity', 'age_group')
        decision_column: Column name for hiring decisions (0=rejected, 1=hired)
        ground_truth_column: Column name for actual qualifications (optional)
        favorable_label: Value representing positive outcome (default: 1)
    
    Returns:
        dict: Comprehensive fairness analysis report
    """
    if applications.empty:
        return {
            'error': 'No application data provided',
            'bias_detected': False
        }
    
    if protected_attribute not in applications.columns:
        return {
            'error': f'Protected attribute "{protected_attribute}" not found in data',
            'bias_detected': False
        }
    
    if decision_column not in applications.columns:
        return {
            'error': f'Decision column "{decision_column}" not found in data',
            'bias_detected': False
        }
    
    # Prepare data
    predictions = applications[decision_column].values
    sensitive_features = applications[protected_attribute].values
    
    # Use ground truth if available, otherwise use decisions as labels
    if ground_truth_column and ground_truth_column in applications.columns:
        labels = applications[ground_truth_column].values
    else:
        # If no ground truth, use a heuristic: assume decisions are correct
        # This is a limitation but allows analysis to proceed
        labels = predictions.copy()
        logger.warning("No ground truth provided. Using decisions as proxy. "
                      "Results may not reflect true fairness.")
    
    # Calculate fairness metrics
    try:
        fm = FairnessMetrics(predictions, labels, sensitive_features, favorable_label)
        metrics = fm.get_all_metrics()
        group_stats = fm.get_group_statistics()
        
        # Detect bias
        bias_analysis = BiasDetector.detect_bias(metrics)
        recommendations = BiasDetector.generate_recommendations(bias_analysis['violations'])
        
        # Calculate fairness score (0-100)
        fairness_score = calculate_fairness_score(metrics)
        
        # Prepare comprehensive report
        report = {
            'summary': {
                'total_applications': len(applications),
                'protected_attribute': protected_attribute,
                'groups_analyzed': list(group_stats.keys()),
                'fairness_score': fairness_score,
                'bias_detected': bias_analysis['bias_detected'],
                'overall_severity': bias_analysis['overall_severity'],
                'total_violations': bias_analysis['total_violations']
            },
            'group_statistics': group_stats,
            'fairness_metrics': metrics,
            'bias_analysis': bias_analysis,
            'recommendations': recommendations,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        return report
        
    except Exception as e:
        logger.error(f"Error in fairness analysis: {str(e)}")
        return {
            'error': f'Fairness analysis failed: {str(e)}',
            'bias_detected': False
        }


def calculate_fairness_score(metrics: Dict[str, Union[float, Dict]]) -> float:
    """
    Calculate overall fairness score (0-100)
    
    Higher score = More fair
    
    Args:
        metrics: Dictionary of fairness metrics
    
    Returns:
        float: Fairness score from 0 to 100
    """
    score = 100.0
    
    # Penalize demographic parity violations
    if metrics['demographic_parity_difference'] > 0.1:
        penalty = min(30, metrics['demographic_parity_difference'] * 100)
        score -= penalty
    
    # Penalize disparate impact violations
    if metrics['demographic_parity_ratio'] < 0.8:
        penalty = min(30, (0.8 - metrics['demographic_parity_ratio']) * 100)
        score -= penalty
    
    # Penalize equal opportunity violations
    if metrics['equal_opportunity_difference'] > 0.1:
        penalty = min(20, metrics['equal_opportunity_difference'] * 100)
        score -= penalty
    
    # Penalize equalized odds violations
    if metrics['average_odds_difference'] > 0.1:
        penalty = min(15, metrics['average_odds_difference'] * 100)
        score -= penalty
    
    # Penalize FPR violations
    if metrics['false_positive_rate_difference'] > 0.1:
        penalty = min(5, metrics['false_positive_rate_difference'] * 50)
        score -= penalty
    
    return max(0.0, round(score, 2))


def get_fairness_badge(fairness_score: float) -> Dict[str, str]:
    """
    Get visual badge for fairness score
    
    Args:
        fairness_score: Score from 0-100
    
    Returns:
        dict: Badge information with level, color, and description
    """
    if fairness_score >= 90:
        return {
            'level': 'A+',
            'label': 'Excellent Fairness',
            'color': '#10b981',  # Green
            'description': 'Hiring process demonstrates excellent fairness across all groups'
        }
    elif fairness_score >= 80:
        return {
            'level': 'A',
            'label': 'Good Fairness',
            'color': '#22c55e',  # Light green
            'description': 'Hiring process is generally fair with minor areas for improvement'
        }
    elif fairness_score >= 70:
        return {
            'level': 'B',
            'label': 'Acceptable Fairness',
            'color': '#eab308',  # Yellow
            'description': 'Hiring process is acceptable but has notable fairness concerns'
        }
    elif fairness_score >= 60:
        return {
            'level': 'C',
            'label': 'Fair Concerns',
            'color': '#f59e0b',  # Orange
            'description': 'Hiring process shows significant fairness issues requiring attention'
        }
    elif fairness_score >= 50:
        return {
            'level': 'D',
            'label': 'Serious Issues',
            'color': '#ef4444',  # Red
            'description': 'Hiring process has serious fairness violations requiring immediate action'
        }
    else:
        return {
            'level': 'F',
            'label': 'Critical Bias',
            'color': '#dc2626',  # Dark red
            'description': 'URGENT: Hiring process shows critical bias. Immediate intervention required'
        }


# Backward compatibility functions (match old API)
def calculate_demographic_parity(selection_rates: Dict[str, float]) -> float:
    """Legacy function for backward compatibility"""
    if not selection_rates or len(selection_rates) < 2:
        return 0.0
    rates = list(selection_rates.values())
    return round(max(rates) - min(rates), 4)


def calculate_equal_opportunity(true_positive_rates: Dict[str, float]) -> float:
    """Legacy function for backward compatibility"""
    if not true_positive_rates or len(true_positive_rates) < 2:
        return 0.0
    rates = list(true_positive_rates.values())
    return round(max(rates) - min(rates), 4)


def calculate_disparate_impact(selection_rates: Dict[str, float]) -> Dict[str, float]:
    """Legacy function for backward compatibility"""
    if not selection_rates or len(selection_rates) < 2:
        return {}
    
    groups = list(selection_rates.keys())
    ratios = {}
    
    for i, group1 in enumerate(groups):
        for group2 in groups[i+1:]:
            rate1 = selection_rates[group1]
            rate2 = selection_rates[group2]
            
            if rate2 > 0:
                ratio = rate1 / rate2
                ratios[f"{group1}_vs_{group2}"] = round(ratio, 4)
    
    return ratios


# Main export - use this function in your routes
__all__ = [
    'FairnessMetrics',
    'BiasDetector',
    'analyze_hiring_fairness_comprehensive',
    'calculate_fairness_score',
    'get_fairness_badge',
    'calculate_demographic_parity',
    'calculate_equal_opportunity',
    'calculate_disparate_impact'
]
