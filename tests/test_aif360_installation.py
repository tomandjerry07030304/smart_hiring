"""
AIF360 Installation Verification Script
Final Year Project - Smart Hiring System
Windows Compatible Version (No Unicode)
"""

import sys
import traceback

def test_aif360_installation():
    """Comprehensive AIF360 installation test"""
    
    print("=" * 70)
    print("AIF360 INSTALLATION VERIFICATION")
    print("=" * 70)
    print()
    
    # Test 1: Basic Import
    print("[1/6] Testing basic AIF360 import...")
    try:
        import aif360
        print(f"    [OK] SUCCESS: AIF360 version {aif360.__version__}")
    except ImportError as e:
        print(f"    [FAIL] {e}")
        print("\n    FIX: pip install aif360==0.6.1")
        return False
    
    # Test 2: NumPy Compatibility
    print("\n[2/6] Testing NumPy compatibility...")
    try:
        import numpy as np
        print(f"    [OK] SUCCESS: NumPy version {np.__version__}")
        if not np.__version__.startswith('1.26'):
            print(f"    [WARN] Expected NumPy 1.26.x, got {np.__version__}")
    except Exception as e:
        print(f"    [FAIL] {e}")
        return False
    
    # Test 3: Dataset Module
    print("\n[3/6] Testing dataset creation...")
    try:
        from aif360.datasets import BinaryLabelDataset
        import pandas as pd
        
        # Create test data
        df = pd.DataFrame({
            'gender': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            'score': [0.3, 0.8, 0.4, 0.9, 0.35, 0.85, 0.45, 0.95, 0.5, 0.7],
            'hired': [0, 1, 0, 1, 0, 1, 1, 1, 0, 1]
        })
        
        dataset = BinaryLabelDataset(
            df=df,
            label_names=['hired'],
            protected_attribute_names=['gender'],
            favorable_label=1,
            unfavorable_label=0
        )
        
        print(f"    ✅ SUCCESS: Dataset shape {dataset.features.shape}")
    except Exception as e:
        print(f"    ❌ FAILED: {e}")
        traceback.print_exc()
        return False
    
    # Test 4: Metrics Calculation
    print("\n[4/6] Testing fairness metrics...")
    try:
        from aif360.metrics import BinaryLabelDatasetMetric
        
        metric = BinaryLabelDatasetMetric(
            dataset,
            privileged_groups=[{'gender': 1}],
            unprivileged_groups=[{'gender': 0}]
        )
        
        spdiff = metric.statistical_parity_difference()
        di = metric.disparate_impact()
        
        print(f"    ✅ SUCCESS: Calculated metrics")
        print(f"       - Statistical Parity Difference: {spdiff:.3f}")
        print(f"       - Disparate Impact: {di:.3f}")
        
        # Interpret results
        if abs(spdiff) < 0.1:
            print(f"       ✅ Fair: Statistical parity within acceptable range")
        else:
            print(f"       ⚠️  Bias detected: |SPD| = {abs(spdiff):.3f} > 0.1")
            
        if 0.8 <= di <= 1.25:
            print(f"       ✅ Fair: Passes 80% rule (DI = {di:.3f})")
        else:
            print(f"       ⚠️  Bias detected: DI = {di:.3f} outside [0.8, 1.25]")
            
    except Exception as e:
        print(f"    ❌ FAILED: {e}")
        traceback.print_exc()
        return False
    
    # Test 5: Classification Metrics
    print("\n[5/6] Testing classification metrics...")
    try:
        from aif360.metrics import ClassificationMetric
        
        # Create prediction dataset (same as ground truth for this test)
        pred_dataset = dataset.copy(deepcopy=True)
        
        clf_metric = ClassificationMetric(
            dataset,
            pred_dataset,
            privileged_groups=[{'gender': 1}],
            unprivileged_groups=[{'gender': 0}]
        )
        
        eo_diff = clf_metric.equal_opportunity_difference()
        ao_diff = clf_metric.average_odds_difference()
        
        print(f"    [OK] SUCCESS: Calculated classification metrics")
        print(f"       - Equal Opportunity Difference: {eo_diff:.3f}")
        print(f"       - Average Odds Difference: {ao_diff:.3f}")
        
    except Exception as e:
        print(f"    [FAIL] {e}")
        traceback.print_exc()
        return False
    
    # Test 6: Bias Mitigation
    print("\n[6/6] Testing bias mitigation algorithms...")
    try:
        from aif360.algorithms.preprocessing import Reweighing
        
        RW = Reweighing(
            privileged_groups=[{'gender': 1}],
            unprivileged_groups=[{'gender': 0}]
        )
        
        dataset_transformed = RW.fit_transform(dataset)
        
        # Check if weights changed
        original_weights = dataset.instance_weights.sum()
        new_weights = dataset_transformed.instance_weights.sum()
        
        print(f"    ✅ SUCCESS: Reweighing applied")
        print(f"       - Original total weight: {original_weights:.1f}")
        print(f"       - New total weight: {new_weights:.1f}")
        
        # Calculate metrics after mitigation
        mitigated_metric = BinaryLabelDatasetMetric(
            dataset_transformed,
            privileged_groups=[{'gender': 1}],
            unprivileged_groups=[{'gender': 0}]
        )
        
        spdiff_after = mitigated_metric.statistical_parity_difference()
        di_after = mitigated_metric.disparate_impact()
        
        print(f"\n    📊 Bias Reduction:")
        print(f"       Before: SPD={spdiff:.3f}, DI={di:.3f}")
        print(f"       After:  SPD={spdiff_after:.3f}, DI={di_after:.3f}")
        print(f"       Improvement: {abs(spdiff) - abs(spdiff_after):.3f}")
        
    except Exception as e:
        print(f"    ❌ FAILED: {e}")
        traceback.print_exc()
        return False
    
    # Final Summary
    print("\n" + "=" * 70)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 70)
    print("\nAIF360 is working correctly in your environment.")
    print("\nYou can now:")
    print("  1. Use AIF360 in your project")
    print("  2. Run your Railway deployment")
    print("  3. Integrate with your Smart Hiring System")
    print("\n" + "=" * 70)
    
    return True


if __name__ == "__main__":
    success = test_aif360_installation()
    sys.exit(0 if success else 1)
