# Fairness Engine Quick Reference Guide

## 🎯 What is this?

A **lightweight fairness evaluation engine** that detects bias in AI-driven hiring decisions. Built specifically for Render deployment (no AIF360 dependency).

---

## 🚀 Quick Start

### 1. Basic Usage

```python
from backend.services.fairness_engine import analyze_hiring_fairness_comprehensive
import pandas as pd

# Your application data
applications_df = pd.DataFrame({
    'gender': ['male', 'female', 'male', 'female', 'male'],
    'decision': [1, 0, 1, 1, 0],  # 1 = hired, 0 = rejected
    'ground_truth': [1, 1, 1, 0, 0]  # actual qualifications
})

# Run fairness analysis
report = analyze_hiring_fairness_comprehensive(
    applications=applications_df,
    protected_attribute='gender',
    decision_column='decision',
    ground_truth_column='ground_truth',  # Optional
    favorable_label=1
)

# Check results
print(f"Bias Detected: {report['summary']['bias_detected']}")
print(f"Fairness Score: {report['summary']['fairness_score']}/100")
print(f"Badge: {report['summary']['badge']}")
```

---

## 📊 Output Structure

### Summary Section
```python
report['summary'] = {
    'total_applications': 156,
    'bias_detected': True,
    'fairness_score': 68.5,  # 0-100 scale
    'badge': 'C - Fair Concerns',
    'protected_groups': ['male', 'female']
}
```

### Fairness Metrics
```python
report['fairness_metrics'] = {
    'demographic_parity_difference': 0.156,  # < 0.1 is fair
    'demographic_parity_ratio': 0.714,       # ~1.0 is fair
    'disparate_impact': {
        'female vs male': 0.72  # >= 0.8 is fair (80% rule)
    },
    'equal_opportunity_difference': 0.089,   # < 0.1 is fair
    'average_odds_difference': 0.067,        # < 0.1 is fair
    'predictive_parity_difference': 0.023,   # < 0.1 is fair
    'false_positive_rate_difference': 0.045,
    'false_negative_rate_difference': 0.112,
    'theil_index': 0.12  # 0 = perfect equality
}
```

### Group Statistics
```python
report['group_statistics'] = {
    'male': {
        'count': 89,
        'selected': 54,
        'selection_rate': 0.607,
        'tpr': 0.812,  # True Positive Rate
        'fpr': 0.134,  # False Positive Rate
        'precision': 0.789
    },
    'female': {
        'count': 67,
        'selected': 29,
        'selection_rate': 0.433,
        'tpr': 0.745,
        'fpr': 0.089,
        'precision': 0.766
    }
}
```

### Bias Analysis
```python
report['bias_analysis'] = {
    'violations': [
        {
            'metric': 'disparate_impact',
            'comparison': 'female vs male',
            'value': 0.72,
            'threshold': 0.8,
            'severity': 'medium',  # critical, high, medium, low
            'affected_groups': ['female']
        }
    ],
    'total_violations': 1,
    'critical_violations': 0,
    'high_violations': 0,
    'medium_violations': 1,
    'low_violations': 0
}
```

### Recommendations
```python
report['recommendations'] = [
    "Disparate impact detected in female vs male (ratio: 0.72). This violates the 80% rule and may indicate discrimination.",
    "Demographic parity difference of 15.6% exceeds the 10% threshold. Review selection criteria to ensure equal treatment.",
    "Consider implementing blind resume screening to reduce demographic bias."
]
```

---

## 🎓 Fairness Metrics Explained

### 1. Demographic Parity (Statistical Parity)
**Question:** Are all groups hired at equal rates?

**Formula:** `P(hired | male) - P(hired | female)`

**Ideal Value:** 0 (no difference)  
**Threshold:** < 0.1 (10% difference is acceptable)

**Example:**
- Males: 60% hired
- Females: 40% hired
- Difference: 0.20 → **VIOLATION**

---

### 2. Disparate Impact (80% Rule)
**Question:** Is the lowest-hired group hired at least 80% as often as the highest-hired group?

**Formula:** `min(selection_rate) / max(selection_rate)`

**Ideal Value:** 1.0 (equal rates)  
**Legal Threshold:** ≥ 0.8 (EEOC rule)

**Example:**
- Males: 100 hired / 100 applicants = 100%
- Females: 79 hired / 100 applicants = 79%
- Ratio: 0.79 < 0.8 → **VIOLATION** (legal concern)

---

### 3. Equal Opportunity
**Question:** Do qualified candidates from all groups have equal chances?

**Formula:** `TPR_male - TPR_female`  
(TPR = True Positive Rate = qualified people who got hired)

**Ideal Value:** 0  
**Threshold:** < 0.1

**Example:**
- Qualified males: 90% hired
- Qualified females: 75% hired
- Difference: 0.15 → **VIOLATION**

---

### 4. Equalized Odds (Average Odds)
**Question:** Does the model make equal mistakes across groups?

**Formula:** `avg(|TPR_diff|, |FPR_diff|)`

**Ideal Value:** 0  
**Threshold:** < 0.1

**Why it matters:** Ensures both qualified and unqualified candidates are treated equally.

---

### 5. Predictive Parity
**Question:** Are positive predictions equally accurate across groups?

**Formula:** `Precision_male - Precision_female`

**Ideal Value:** 0  
**Threshold:** < 0.1

**Example:**
- Males hired: 80% were actually qualified
- Females hired: 60% were actually qualified
- Difference: 0.20 → System favors males

---

### 6. Theil Index
**Question:** How unequally are benefits distributed?

**Range:** [0, ∞)  
**Ideal Value:** 0 (perfect equality)

**Interpretation:**
- 0.0-0.1: Low inequality
- 0.1-0.2: Moderate inequality
- > 0.2: High inequality

---

## 🚨 Severity Levels

### Critical (Immediate Action Required)
- Disparate Impact < 0.5 (hiring rate < 50% of reference group)
- Demographic Parity > 0.3 (30%+ difference)
- Equal Opportunity > 0.3

### High (Serious Concern)
- Disparate Impact 0.5-0.7
- Demographic Parity 0.2-0.3
- Equal Opportunity 0.2-0.3

### Medium (Needs Attention)
- Disparate Impact 0.7-0.8 (borderline 80% rule)
- Demographic Parity 0.1-0.2
- Equal Opportunity 0.1-0.2

### Low (Monitor)
- Minor deviations below thresholds
- Within acceptable ranges but not perfect

---

## 📈 Fairness Score & Badges

### Score Calculation
```
Fairness Score = 100 × (1 - normalized_penalty)

Where penalty considers:
- Demographic Parity violations (weight: 0.25)
- Disparate Impact violations (weight: 0.30)
- Equal Opportunity violations (weight: 0.20)
- Average Odds violations (weight: 0.15)
- Other metrics (weight: 0.10)
```

### Badge System
| Score | Badge | Level | Color | Meaning |
|-------|-------|-------|-------|---------|
| 90-100 | Excellent Fairness | A+ | 🟢 Green | No significant bias detected |
| 80-89 | Good Fairness | A | 🟢 Light Green | Minor issues, generally fair |
| 70-79 | Acceptable Fairness | B | 🟡 Yellow | Some concerns, needs monitoring |
| 60-69 | Fair Concerns | C | 🟠 Orange | Significant issues, action needed |
| 50-59 | Serious Issues | D | 🔴 Red | Major bias detected |
| 0-49 | Critical Bias | F | 🔴 Dark Red | Immediate action required |

---

## 💻 API Integration

### Flask Route Example

```python
from flask import Blueprint, request, jsonify
from backend.services.fairness_engine import analyze_hiring_fairness_comprehensive
from backend.models.fairness import FairnessAudit
import pandas as pd

fairness_bp = Blueprint('fairness', __name__)

@fairness_bp.route('/api/jobs/<job_id>/fairness-report', methods=['POST'])
def generate_fairness_report(job_id):
    data = request.json
    protected_attr = data.get('protected_attribute', 'gender')
    
    # Fetch applications from database
    applications = Application.find_by_job_id(job_id)
    
    # Convert to DataFrame
    df = pd.DataFrame([{
        protected_attr: app.candidate.get(protected_attr),
        'decision': 1 if app.status == 'hired' else 0,
        'ground_truth': app.actual_qualification_score  # if available
    } for app in applications])
    
    # Run analysis
    report = analyze_hiring_fairness_comprehensive(
        applications=df,
        protected_attribute=protected_attr,
        decision_column='decision',
        ground_truth_column='ground_truth'
    )
    
    # Save audit to database
    audit = FairnessAudit(
        job_id=job_id,
        protected_attribute=protected_attr,
        fairness_score=report['summary']['fairness_score'],
        metrics=report['fairness_metrics'],
        violations=report['bias_analysis']['violations']
    )
    audit.save()
    
    return jsonify(report), 200
```

---

## 🔧 Advanced Usage

### Custom Thresholds

```python
from backend.services.fairness_engine import BiasDetector

# Modify thresholds
BiasDetector.THRESHOLDS['demographic_parity_difference'] = 0.05  # Stricter (5%)
BiasDetector.THRESHOLDS['disparate_impact'] = 0.85  # More lenient (85% rule)

# Run analysis with custom thresholds
report = analyze_hiring_fairness_comprehensive(...)
```

### Individual Metric Calculation

```python
from backend.services.fairness_engine import FairnessMetrics
import numpy as np

predictions = np.array([1, 0, 1, 1, 0])
labels = np.array([1, 1, 1, 0, 0])
sensitive = np.array(['male', 'female', 'male', 'female', 'male'])

metrics = FairnessMetrics(predictions, labels, sensitive, favorable_label=1)

# Calculate specific metrics
dp_diff = metrics.demographic_parity_difference()
di = metrics.disparate_impact()
eo_diff = metrics.equal_opportunity_difference()

print(f"Demographic Parity: {dp_diff:.3f}")
print(f"Disparate Impact: {di}")
print(f"Equal Opportunity: {eo_diff:.3f}")
```

### Backward Compatibility Functions

```python
from backend.services.fairness_engine import (
    calculate_demographic_parity,
    calculate_equal_opportunity,
    calculate_disparate_impact
)

# Legacy API (still works)
selection_rates = {'male': 0.60, 'female': 0.45}
dp = calculate_demographic_parity(selection_rates)  # Returns max - min

tpr_by_group = {'male': 0.85, 'female': 0.72}
eo = calculate_equal_opportunity(tpr_by_group)  # Returns max - min

di = calculate_disparate_impact(selection_rates)  # Returns ratios dict
```

---

## 🎨 Frontend Display Example

### JavaScript Integration

```javascript
async function displayFairnessReport(jobId) {
    const response = await fetch(`/api/jobs/${jobId}/fairness-report`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({protected_attribute: 'gender'})
    });
    
    const report = await response.json();
    
    // Display badge
    const badgeColor = getBadgeColor(report.summary.badge);
    document.getElementById('fairness-badge').innerHTML = `
        <div class="badge badge-${badgeColor}">
            ${report.summary.badge}
            <span class="score">${report.summary.fairness_score.toFixed(1)}/100</span>
        </div>
    `;
    
    // Display violations
    if (report.summary.bias_detected) {
        const violationsHtml = report.bias_analysis.violations.map(v => `
            <div class="violation violation-${v.severity}">
                <strong>${v.metric}</strong>: ${v.comparison}
                <br>Value: ${v.value.toFixed(3)} (threshold: ${v.threshold})
            </div>
        `).join('');
        document.getElementById('violations').innerHTML = violationsHtml;
    }
    
    // Display recommendations
    const recsHtml = report.recommendations.map(r => `
        <li class="recommendation">${r}</li>
    `).join('');
    document.getElementById('recommendations').innerHTML = `<ul>${recsHtml}</ul>`;
    
    // Create group comparison chart
    createFairnessChart(report.group_statistics);
}

function getBadgeColor(badge) {
    if (badge.startsWith('A')) return 'success';
    if (badge.startsWith('B')) return 'info';
    if (badge.startsWith('C')) return 'warning';
    return 'danger';
}
```

---

## ❓ Frequently Asked Questions

### Q1: Which metric should I prioritize?
**A:** Depends on your use case:
- **Legal compliance:** Disparate Impact (80% rule)
- **Equal treatment:** Demographic Parity
- **Qualified candidates:** Equal Opportunity
- **Overall fairness:** Average Odds Difference

### Q2: Can all metrics be satisfied simultaneously?
**A:** No. Research shows it's mathematically impossible to satisfy all fairness definitions at once (see Impossibility Theorems). Choose metrics based on your organization's values.

### Q3: What if ground_truth is unavailable?
**A:** You can still calculate:
- Demographic Parity
- Disparate Impact

But you cannot calculate:
- Equal Opportunity (needs actual qualifications)
- Equalized Odds (needs actual qualifications)

### Q4: How to handle missing protected attributes?
**A:** Options:
1. Exclude rows with missing values
2. Infer from other data (careful - can introduce bias)
3. Create "Unknown" category (include in analysis)

### Q5: What if I have more than 2 groups?
**A:** The engine handles multiple groups automatically. Metrics compare all pairs:
```python
groups = ['male', 'female', 'non-binary']
# Will compare: male vs female, male vs non-binary, female vs non-binary
```

---

## 🐛 Troubleshooting

### Issue: "Empty DataFrame" Error
```python
# Problem: No data in applications_df
# Solution: Check filters and ensure data exists
if applications_df.empty:
    return {'error': 'No applications to analyze'}
```

### Issue: All metrics return 0 or NaN
```python
# Problem: No variance in data (all same decision)
# Solution: Verify decisions have both 0 and 1 values
print(applications_df['decision'].value_counts())
```

### Issue: Ground truth not recognized
```python
# Problem: Column name mismatch
# Solution: Check exact column name
print(applications_df.columns)  # See available columns
report = analyze_hiring_fairness_comprehensive(
    applications=applications_df,
    ground_truth_column='actual_qualification'  # Exact name
)
```

---

## 📚 Further Reading

1. **Academic Papers:**
   - Hardt et al. (2016): "Equality of Opportunity in Supervised Learning"
   - Chouldechova (2017): "Fair Prediction with Disparate Impact"

2. **Legal Resources:**
   - EEOC Uniform Guidelines on Employee Selection Procedures
   - EU AI Act (Proposed)

3. **Technical Documentation:**
   - Full implementation: `backend/services/fairness_engine.py`
   - FYP Report: `FAIRNESS_IMPLEMENTATION_FYP_REPORT.md`

---

## 📞 Support

For questions or issues:
1. Check this guide first
2. Review code comments in `fairness_engine.py`
3. Check FYP report for mathematical details
4. Contact project maintainer

---

**Version:** 1.0  
**Last Updated:** January 2024  
**Part of:** Smart Hiring System - Final Year Project
