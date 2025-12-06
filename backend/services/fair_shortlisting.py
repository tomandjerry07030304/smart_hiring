"""
Fairness-Aware Shortlisting Service
====================================
Implements bias mitigation algorithms for candidate shortlisting

Based on research from:
- Fabris et al. (2025): Fairness and Bias in Algorithmic Hiring
- AIF360 Reweighing Algorithm (Kamiran & Calders, 2012)
- 80% Rule (EEOC Uniform Guidelines on Employee Selection)

Author: Smart Hiring System Team
Date: December 2025
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FairShortlistingEngine:
    """
    Fairness-aware candidate shortlisting engine
    
    Implements multiple fairness algorithms:
    1. Post-processing: Adjusts shortlist after scoring (80% rule)
    2. Re-weighting: Adjusts scores based on group representation
    3. Threshold optimization: Finds fair cutoff scores per group
    """
    
    def __init__(self, threshold: float = 0.8, protected_attributes: List[str] = None):
        """
        Initialize fairness engine
        
        Args:
            threshold: Minimum disparate impact ratio (default: 0.8 for 80% rule)
            protected_attributes: List of protected attribute names (e.g., ['gender', 'ethnicity'])
        """
        self.threshold = threshold
        self.protected_attributes = protected_attributes or ['gender']
        
    
    def fair_shortlist_postprocessing(
        self, 
        candidates: List[Dict[str, Any]], 
        protected_attribute: str,
        selection_percentage: float = 0.20,
        score_key: str = 'overall_score'
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Apply post-processing fairness to shortlist
        
        Algorithm:
        1. Score all candidates normally
        2. Sort by score and select top N%
        3. Calculate disparate impact ratio
        4. If ratio < threshold, adjust shortlist to meet fairness constraint
        
        Args:
            candidates: List of candidate dictionaries with scores
            protected_attribute: Name of protected attribute (e.g., 'gender')
            selection_percentage: Percentage of candidates to shortlist (default: 20%)
            score_key: Key name for candidate score in dict
            
        Returns:
            Tuple of (shortlisted_candidates, fairness_report)
        """
        if not candidates:
            return [], {'error': 'No candidates provided'}
        
        if len(candidates) < 5:
            logger.warning("Too few candidates for fairness analysis")
            # Just return top candidates without fairness adjustment
            sorted_candidates = sorted(candidates, key=lambda x: x.get(score_key, 0), reverse=True)
            n_select = max(1, int(len(candidates) * selection_percentage))
            return sorted_candidates[:n_select], {
                'warning': 'Too few candidates for fairness analysis',
                'total_candidates': len(candidates)
            }
        
        # Sort by score
        sorted_candidates = sorted(candidates, key=lambda x: x.get(score_key, 0), reverse=True)
        
        # Calculate initial selection size
        n_select = max(1, int(len(candidates) * selection_percentage))
        initial_shortlist = sorted_candidates[:n_select]
        
        # Extract protected attribute values
        groups = set()
        for c in candidates:
            group_val = c.get(protected_attribute, 'unknown')
            groups.add(group_val)
        
        # Remove 'unknown' if it exists and there are other groups
        if 'unknown' in groups and len(groups) > 1:
            # Don't use unknown for fairness calculation
            groups.discard('unknown')
        
        if len(groups) < 2:
            logger.info(f"Only one group found for {protected_attribute}, no fairness adjustment needed")
            return initial_shortlist, {
                'single_group': True,
                'total_candidates': len(candidates),
                'shortlisted': len(initial_shortlist)
            }
        
        # Calculate selection rates per group
        selection_rates = {}
        group_counts = {}
        
        for group in groups:
            # Total in group
            group_total = len([c for c in candidates if c.get(protected_attribute) == group])
            # Selected from group
            group_selected = len([c for c in initial_shortlist if c.get(protected_attribute) == group])
            
            if group_total > 0:
                selection_rates[group] = group_selected / group_total
                group_counts[group] = {
                    'total': group_total,
                    'selected': group_selected,
                    'rate': selection_rates[group]
                }
        
        # Calculate disparate impact
        if len(selection_rates) < 2:
            return initial_shortlist, {
                'insufficient_groups': True,
                'group_counts': group_counts
            }
        
        min_rate = min(selection_rates.values())
        max_rate = max(selection_rates.values())
        di_ratio = min_rate / max_rate if max_rate > 0 else 0
        
        # Identify groups
        underrep_group = min(selection_rates, key=selection_rates.get)
        overrep_group = max(selection_rates, key=selection_rates.get)
        
        logger.info(f"Disparate Impact Ratio: {di_ratio:.3f} (threshold: {self.threshold})")
        logger.info(f"Underrepresented: {underrep_group} ({selection_rates[underrep_group]:.2%})")
        logger.info(f"Overrepresented: {overrep_group} ({selection_rates[overrep_group]:.2%})")
        
        # Check if adjustment needed
        if di_ratio >= self.threshold:
            logger.info("✅ Fairness constraint satisfied - no adjustment needed")
            return initial_shortlist, {
                'fair': True,
                'di_ratio': di_ratio,
                'threshold': self.threshold,
                'group_counts': group_counts,
                'adjustment_made': False
            }
        
        # Apply fairness adjustment
        logger.warning(f"⚠️ Fairness violation detected (DI ratio: {di_ratio:.3f} < {self.threshold})")
        logger.info("🔧 Applying post-processing fairness adjustment...")
        
        # Calculate how many to swap
        # Goal: Increase underrepresented group's selection rate
        target_rate = max_rate * self.threshold
        target_selected = int(np.ceil(target_rate * group_counts[underrep_group]['total']))
        current_selected = group_counts[underrep_group]['selected']
        need_to_add = max(0, target_selected - current_selected)
        
        # Find candidates from underrepresented group not in shortlist
        underrep_not_selected = [
            c for c in sorted_candidates[n_select:] 
            if c.get(protected_attribute) == underrep_group
        ]
        
        # Add top-scoring from underrepresented group
        additional = underrep_not_selected[:need_to_add]
        
        # Remove lowest-scoring from overrepresented group
        overrep_in_shortlist = [
            (i, c) for i, c in enumerate(initial_shortlist) 
            if c.get(protected_attribute) == overrep_group
        ]
        
        # Sort by score (ascending to get lowest first)
        overrep_in_shortlist.sort(key=lambda x: x[1].get(score_key, 0))
        
        # Remove lowest scoring from overrepresented group
        to_remove = min(need_to_add, len(overrep_in_shortlist))
        remove_indices = set(idx for idx, _ in overrep_in_shortlist[:to_remove])
        
        # Build final shortlist
        final_shortlist = [c for i, c in enumerate(initial_shortlist) if i not in remove_indices]
        final_shortlist.extend(additional)
        
        # Recalculate metrics
        final_selection_rates = {}
        final_group_counts = {}
        
        for group in groups:
            group_total = len([c for c in candidates if c.get(protected_attribute) == group])
            group_selected = len([c for c in final_shortlist if c.get(protected_attribute) == group])
            
            if group_total > 0:
                final_selection_rates[group] = group_selected / group_total
                final_group_counts[group] = {
                    'total': group_total,
                    'selected': group_selected,
                    'rate': final_selection_rates[group]
                }
        
        final_di_ratio = min(final_selection_rates.values()) / max(final_selection_rates.values())
        
        logger.info(f"✅ Adjustment complete - new DI ratio: {final_di_ratio:.3f}")
        
        fairness_report = {
            'fair': final_di_ratio >= self.threshold,
            'adjustment_made': True,
            'before': {
                'di_ratio': di_ratio,
                'group_counts': group_counts
            },
            'after': {
                'di_ratio': final_di_ratio,
                'group_counts': final_group_counts
            },
            'changes': {
                'added_from_underrep': len(additional),
                'removed_from_overrep': to_remove,
                'underrep_group': underrep_group,
                'overrep_group': overrep_group
            },
            'threshold': self.threshold
        }
        
        return final_shortlist, fairness_report
    
    
    def fair_shortlist_reweighting(
        self,
        candidates: List[Dict[str, Any]],
        protected_attribute: str,
        score_key: str = 'overall_score'
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Apply re-weighting algorithm for fairness
        
        Based on Kamiran & Calders (2012) reweighting algorithm.
        Adjusts candidate scores based on group representation to achieve
        demographic parity.
        
        Args:
            candidates: List of candidate dictionaries
            protected_attribute: Name of protected attribute
            score_key: Key name for score
            
        Returns:
            Tuple of (candidates_with_fair_scores, fairness_report)
        """
        if not candidates or len(candidates) < 5:
            return candidates, {'warning': 'Too few candidates for reweighting'}
        
        # Calculate group statistics
        groups = defaultdict(lambda: {'count': 0, 'avg_score': 0.0, 'scores': []})
        
        for c in candidates:
            group = c.get(protected_attribute, 'unknown')
            score = c.get(score_key, 0)
            groups[group]['count'] += 1
            groups[group]['scores'].append(score)
        
        # Calculate average scores per group
        for group in groups:
            if groups[group]['count'] > 0:
                groups[group]['avg_score'] = np.mean(groups[group]['scores'])
        
        # Remove unknown if multiple groups exist
        if 'unknown' in groups and len(groups) > 1:
            del groups['unknown']
        
        if len(groups) < 2:
            return candidates, {'single_group': True}
        
        # Calculate probabilities
        total_candidates = sum(g['count'] for g in groups.values())
        for group in groups:
            groups[group]['prob'] = groups[group]['count'] / total_candidates
        
        # Expected probability (equal representation)
        expected_prob = 1.0 / len(groups)
        
        # Calculate reweighting factors
        for group in groups:
            groups[group]['weight'] = expected_prob / groups[group]['prob']
        
        logger.info("📊 Reweighting factors calculated:")
        for group, stats in groups.items():
            logger.info(f"  {group}: weight={stats['weight']:.3f} (prob={stats['prob']:.2%}, expected={expected_prob:.2%})")
        
        # Apply weights to scores
        reweighted_candidates = []
        for c in candidates:
            group = c.get(protected_attribute, 'unknown')
            if group in groups:
                original_score = c.get(score_key, 0)
                weight = groups[group]['weight']
                fair_score = original_score * weight
                
                # Create copy with fair score
                c_copy = c.copy()
                c_copy['original_score'] = original_score
                c_copy['fair_score'] = fair_score
                c_copy['reweight_factor'] = weight
                reweighted_candidates.append(c_copy)
            else:
                reweighted_candidates.append(c)
        
        # Sort by fair score
        reweighted_candidates.sort(key=lambda x: x.get('fair_score', x.get(score_key, 0)), reverse=True)
        
        fairness_report = {
            'method': 'reweighting',
            'groups': {
                group: {
                    'count': stats['count'],
                    'probability': stats['prob'],
                    'weight': stats['weight'],
                    'avg_original_score': stats['avg_score']
                }
                for group, stats in groups.items()
            },
            'expected_probability': expected_prob
        }
        
        return reweighted_candidates, fairness_report
    
    
    def fair_shortlist_threshold_optimization(
        self,
        candidates: List[Dict[str, Any]],
        protected_attribute: str,
        target_selection: int,
        score_key: str = 'overall_score'
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Optimize selection thresholds per group for fairness
        
        Algorithm:
        1. Calculate separate score thresholds for each group
        2. Select top candidates from each group proportionally
        3. Ensures equal selection rates across groups
        
        Args:
            candidates: List of candidate dictionaries
            protected_attribute: Protected attribute name
            target_selection: Total number to select
            score_key: Score key name
            
        Returns:
            Tuple of (shortlisted_candidates, fairness_report)
        """
        if not candidates or len(candidates) < target_selection:
            sorted_cands = sorted(candidates, key=lambda x: x.get(score_key, 0), reverse=True)
            return sorted_cands[:target_selection], {'warning': 'Insufficient candidates'}
        
        # Group candidates
        grouped = defaultdict(list)
        for c in candidates:
            group = c.get(protected_attribute, 'unknown')
            grouped[group].append(c)
        
        # Remove unknown if multiple groups
        if 'unknown' in grouped and len(grouped) > 1:
            del grouped['unknown']
        
        if len(grouped) < 2:
            sorted_cands = sorted(candidates, key=lambda x: x.get(score_key, 0), reverse=True)
            return sorted_cands[:target_selection], {'single_group': True}
        
        # Calculate proportional selection per group
        # Goal: Equal selection RATE across groups (demographic parity)
        group_sizes = {group: len(cands) for group, cands in grouped.items()}
        
        # Target selection rate
        target_rate = target_selection / len(candidates)
        
        # Calculate selections per group
        group_selections = {}
        for group, size in group_sizes.items():
            group_selections[group] = int(np.round(size * target_rate))
        
        # Adjust to match exact target
        total_selected = sum(group_selections.values())
        if total_selected != target_selection:
            diff = target_selection - total_selected
            # Adjust largest group
            largest_group = max(group_sizes, key=group_sizes.get)
            group_selections[largest_group] += diff
        
        logger.info(f"🎯 Target selections per group (rate={target_rate:.2%}):")
        for group, n_select in group_selections.items():
            logger.info(f"  {group}: {n_select}/{group_sizes[group]} ({n_select/group_sizes[group]:.2%})")
        
        # Select top N from each group
        shortlist = []
        thresholds = {}
        
        for group, n_select in group_selections.items():
            group_cands = sorted(grouped[group], key=lambda x: x.get(score_key, 0), reverse=True)
            selected = group_cands[:n_select]
            shortlist.extend(selected)
            
            if selected:
                thresholds[group] = selected[-1].get(score_key, 0)
        
        # Sort final shortlist by score
        shortlist.sort(key=lambda x: x.get(score_key, 0), reverse=True)
        
        fairness_report = {
            'method': 'threshold_optimization',
            'target_selection_rate': target_rate,
            'group_selections': {
                group: {
                    'total': group_sizes[group],
                    'selected': group_selections[group],
                    'rate': group_selections[group] / group_sizes[group],
                    'threshold': thresholds.get(group, 0)
                }
                for group in grouped.keys()
            },
            'total_selected': len(shortlist)
        }
        
        return shortlist, fairness_report


def apply_fair_shortlisting(
    candidates: List[Dict[str, Any]],
    method: str = 'postprocessing',
    protected_attribute: str = 'gender',
    selection_percentage: float = 0.20,
    threshold: float = 0.8
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Convenience function to apply fair shortlisting
    
    Args:
        candidates: List of candidates with scores
        method: 'postprocessing', 'reweighting', or 'threshold_optimization'
        protected_attribute: Protected attribute name
        selection_percentage: Percentage to shortlist (for postprocessing/reweighting)
        threshold: Disparate impact threshold (default: 0.8)
        
    Returns:
        Tuple of (shortlisted_candidates, fairness_report)
    """
    engine = FairShortlistingEngine(threshold=threshold)
    
    if method == 'postprocessing':
        return engine.fair_shortlist_postprocessing(
            candidates, 
            protected_attribute, 
            selection_percentage
        )
    elif method == 'reweighting':
        reweighted, report = engine.fair_shortlist_reweighting(
            candidates,
            protected_attribute
        )
        # Select top N after reweighting
        n_select = max(1, int(len(candidates) * selection_percentage))
        return reweighted[:n_select], report
    elif method == 'threshold_optimization':
        target_n = max(1, int(len(candidates) * selection_percentage))
        return engine.fair_shortlist_threshold_optimization(
            candidates,
            protected_attribute,
            target_n
        )
    else:
        raise ValueError(f"Unknown method: {method}")


if __name__ == '__main__':
    # Example usage
    print("🧪 Testing Fair Shortlisting Engine\n")
    
    # Mock candidates
    candidates = [
        {'id': 1, 'name': 'Candidate A', 'gender': 'male', 'overall_score': 95},
        {'id': 2, 'name': 'Candidate B', 'gender': 'male', 'overall_score': 90},
        {'id': 3, 'name': 'Candidate C', 'gender': 'female', 'overall_score': 88},
        {'id': 4, 'name': 'Candidate D', 'gender': 'male', 'overall_score': 85},
        {'id': 5, 'name': 'Candidate E', 'gender': 'male', 'overall_score': 82},
        {'id': 6, 'name': 'Candidate F', 'gender': 'female', 'overall_score': 80},
        {'id': 7, 'name': 'Candidate G', 'gender': 'male', 'overall_score': 78},
        {'id': 8, 'name': 'Candidate H', 'gender': 'female', 'overall_score': 75},
        {'id': 9, 'name': 'Candidate I', 'gender': 'male', 'overall_score': 72},
        {'id': 10, 'name': 'Candidate J', 'gender': 'female', 'overall_score': 70},
    ]
    
    print("📊 Original Candidates:")
    for c in candidates:
        print(f"  {c['name']}: {c['gender']} - {c['overall_score']}")
    
    print("\n" + "="*60)
    print("Method 1: Post-Processing Fairness")
    print("="*60)
    
    shortlist, report = apply_fair_shortlisting(
        candidates,
        method='postprocessing',
        selection_percentage=0.4
    )
    
    print(f"\n✅ Shortlisted {len(shortlist)} candidates:")
    for c in shortlist:
        print(f"  {c['name']}: {c['gender']} - {c['overall_score']}")
    
    print(f"\n📈 Fairness Report:")
    print(f"  Fair: {report.get('fair', False)}")
    print(f"  DI Ratio: {report.get('after', {}).get('di_ratio', 0):.3f}")
    print(f"  Adjustment Made: {report.get('adjustment_made', False)}")
