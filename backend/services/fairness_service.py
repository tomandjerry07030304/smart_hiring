"""
Fairness and Bias Detection Service
Uses IBM AIF360 toolkit for fairness metrics
"""

import numpy as np
import pandas as pd
from collections import defaultdict

try:
    from aif360.datasets import BinaryLabelDataset
    from aif360.metrics import BinaryLabelDatasetMetric, ClassificationMetric
    AIF360_AVAILABLE = True
except ImportError:
    AIF360_AVAILABLE = False
    print("Warning: AIF360 not available. Install with: pip install aif360")

def calculate_demographic_parity(selection_rates):
    """
    Calculate demographic parity difference
    
    Demographic Parity: P(Ŷ=1|D=unprivileged) = P(Ŷ=1|D=privileged)
    
    Args:
        selection_rates: dict with {group: selection_rate}
    
    Returns:
        float: Parity difference (0 = perfect parity)
    """
    if not selection_rates or len(selection_rates) < 2:
        return 0.0
    
    rates = list(selection_rates.values())
    max_rate = max(rates)
    min_rate = min(rates)
    
    parity_diff = max_rate - min_rate
    return round(parity_diff, 4)

def calculate_equal_opportunity(true_positive_rates):
    """
    Calculate equal opportunity difference
    
    Equal Opportunity: P(Ŷ=1|Y=1,D=unprivileged) = P(Ŷ=1|Y=1,D=privileged)
    
    Args:
        true_positive_rates: dict with {group: TPR}
    
    Returns:
        float: Opportunity difference (0 = perfect equality)
    """
    if not true_positive_rates or len(true_positive_rates) < 2:
        return 0.0
    
    rates = list(true_positive_rates.values())
    max_rate = max(rates)
    min_rate = min(rates)
    
    opportunity_diff = max_rate - min_rate
    return round(opportunity_diff, 4)

def calculate_disparate_impact(selection_rates):
    """
    Calculate disparate impact ratio
    
    Disparate Impact = P(Ŷ=1|D=unprivileged) / P(Ŷ=1|D=privileged)
    
    A value < 0.8 indicates potential discrimination (80% rule)
    
    Args:
        selection_rates: dict with {group: selection_rate}
    
    Returns:
        dict: Disparate impact ratios
    """
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

def analyze_hiring_fairness(applications_df, protected_attribute='gender', favorable_label=1):
    """
    Comprehensive fairness analysis of hiring decisions
    
    Args:
        applications_df: DataFrame with columns [protected_attribute, decision, ground_truth]
        protected_attribute: Column name for protected attribute (e.g., 'gender', 'race')
        favorable_label: Label for positive outcome (e.g., 1 for hired, 0 for rejected)
    
    Returns:
        dict: Fairness metrics and recommendations
    """
    if applications_df.empty:
        return {
            'error': 'No data provided',
            'bias_detected': False
        }
    
    results = {
        'total_applications': len(applications_df),
        'demographic_breakdown': {},
        'selection_rates': {},
        'fairness_metrics': {},
        'bias_detected': False,
        'bias_groups': [],
        'recommendations': []
    }
    
    # Group statistics
    groups = applications_df[protected_attribute].unique()
    
    for group in groups:
        group_data = applications_df[applications_df[protected_attribute] == group]
        total = len(group_data)
        selected = len(group_data[group_data['decision'] == favorable_label])
        selection_rate = selected / total if total > 0 else 0
        
        results['demographic_breakdown'][str(group)] = total
        results['selection_rates'][str(group)] = round(selection_rate, 4)
    
    # Calculate fairness metrics
    demographic_parity = calculate_demographic_parity(results['selection_rates'])
    disparate_impact = calculate_disparate_impact(results['selection_rates'])
    
    results['fairness_metrics']['demographic_parity_difference'] = demographic_parity
    results['fairness_metrics']['disparate_impact_ratios'] = disparate_impact
    
    # Check for bias
    PARITY_THRESHOLD = 0.1  # 10% difference threshold
    DISPARATE_IMPACT_THRESHOLD = 0.8  # 80% rule
    
    if demographic_parity > PARITY_THRESHOLD:
        results['bias_detected'] = True
        results['bias_groups'].append({
            'type': 'demographic_parity',
            'severity': 'high' if demographic_parity > 0.2 else 'medium',
            'difference': demographic_parity
        })
        results['recommendations'].append(
            f"Demographic parity violation detected ({demographic_parity:.2%} difference). "
            f"Review selection criteria to ensure equal treatment across groups."
        )
    
    # Check disparate impact
    for comparison, ratio in disparate_impact.items():
        if ratio < DISPARATE_IMPACT_THRESHOLD:
            results['bias_detected'] = True
            results['bias_groups'].append({
                'type': 'disparate_impact',
                'comparison': comparison,
                'ratio': ratio,
                'severity': 'high' if ratio < 0.6 else 'medium'
            })
            results['recommendations'].append(
                f"Disparate impact detected in {comparison} (ratio: {ratio:.2f}). "
                f"This violates the 80% rule and may indicate discrimination."
            )
    
    # Calculate equal opportunity if ground truth is available
    if 'ground_truth' in applications_df.columns:
        tpr_by_group = {}
        for group in groups:
            group_data = applications_df[applications_df[protected_attribute] == group]
            positives = group_data[group_data['ground_truth'] == favorable_label]
            
            if len(positives) > 0:
                true_positives = len(positives[positives['decision'] == favorable_label])
                tpr = true_positives / len(positives)
                tpr_by_group[str(group)] = tpr
        
        if tpr_by_group:
            equal_opp = calculate_equal_opportunity(tpr_by_group)
            results['fairness_metrics']['equal_opportunity_difference'] = equal_opp
            
            if equal_opp > PARITY_THRESHOLD:
                results['bias_detected'] = True
                results['recommendations'].append(
                    f"Equal opportunity violation detected ({equal_opp:.2%} difference). "
                    f"Qualified candidates from different groups have unequal chances."
                )
    
    return results

def generate_fairness_report(job_id, applications_data, protected_attributes=['gender', 'age_group', 'ethnicity']):
    """
    Generate comprehensive fairness audit report
    
    Args:
        job_id: Job posting ID
        applications_data: List of application dicts
        protected_attributes: List of attributes to check for fairness
    
    Returns:
        dict: Complete fairness audit report
    """
    df = pd.DataFrame(applications_data)
    
    report = {
        'job_id': job_id,
        'audit_date': pd.Timestamp.now().isoformat(),
        'total_applications': len(df),
        'analyses': {},
        'overall_bias_detected': False,
        'summary_recommendations': []
    }
    
    for attribute in protected_attributes:
        if attribute in df.columns:
            analysis = analyze_hiring_fairness(df, protected_attribute=attribute)
            report['analyses'][attribute] = analysis
            
            if analysis.get('bias_detected'):
                report['overall_bias_detected'] = True
    
    # Generate summary recommendations
    if report['overall_bias_detected']:
        report['summary_recommendations'] = [
            "Implement blind resume screening to remove identifiable information",
            "Use structured interviews with standardized questions",
            "Diversify the interview panel",
            "Set diversity hiring goals and track progress",
            "Regular fairness audits using this tool",
            "Train recruiters on unconscious bias"
        ]
    else:
        report['summary_recommendations'] = [
            "Continue monitoring hiring outcomes for fairness",
            "Maintain current fair hiring practices",
            "Conduct periodic fairness audits"
        ]
    
    return report

def get_fairness_badge(fairness_score):
    """
    Get fairness badge based on metrics
    
    Args:
        fairness_score: Score from 0-100 (100 = perfectly fair)
    
    Returns:
        dict: Badge information
    """
    if fairness_score >= 90:
        return {
            'badge': 'Excellent Fairness',
            'color': 'green',
            'level': 'A+'
        }
    elif fairness_score >= 80:
        return {
            'badge': 'Good Fairness',
            'color': 'lightgreen',
            'level': 'A'
        }
    elif fairness_score >= 70:
        return {
            'badge': 'Acceptable Fairness',
            'color': 'yellow',
            'level': 'B'
        }
    elif fairness_score >= 60:
        return {
            'badge': 'Fair Concerns',
            'color': 'orange',
            'level': 'C'
        }
    else:
        return {
            'badge': 'Serious Bias Issues',
            'color': 'red',
            'level': 'F'
        }
