"""
Enterprise-Grade Fairness Analysis API using AIF360
Production-ready system for bias detection in hiring
Author: Senior AI Architect
License: MIT
"""

import logging
import time
from typing import Dict, List, Optional, Union
from datetime import datetime

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import uvicorn

# AIF360 Imports - The core fairness library
try:
    from aif360.datasets import BinaryLabelDataset, StructuredDataset
    from aif360.metrics import BinaryLabelDatasetMetric, ClassificationMetric
    from aif360.algorithms.preprocessing import Reweighing
    from aif360.algorithms.postprocessing import CalibratedEqOddsPostprocessing, EqOddsPostprocessing
    AIF360_AVAILABLE = True
except ImportError as e:
    logging.error(f"CRITICAL: AIF360 not available: {e}")
    AIF360_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI application
app = FastAPI(
    title="Enterprise Fairness Analysis API",
    description="AIF360-powered bias detection for AI-driven hiring systems",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global metrics for monitoring
METRICS = {
    "total_requests": 0,
    "failed_requests": 0,
    "total_analysis_time": 0.0,
    "analyses_completed": 0
}

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class Application(BaseModel):
    """Single job application record"""
    protected_attribute: Union[str, int, float] = Field(
        ..., 
        description="Value of protected attribute (e.g., 'male', 'female', 0, 1)"
    )
    decision: int = Field(
        ..., 
        description="Hiring decision: 1 = hired/selected, 0 = rejected",
        ge=0,
        le=1
    )
    ground_truth: Optional[int] = Field(
        None,
        description="Actual qualification: 1 = qualified, 0 = unqualified",
        ge=0,
        le=1
    )
    
    @validator('decision', 'ground_truth')
    def validate_binary(cls, v):
        if v is not None and v not in [0, 1]:
            raise ValueError('Must be 0 or 1')
        return v


class AnalysisRequest(BaseModel):
    """Request payload for fairness analysis"""
    applications: List[Application] = Field(
        ..., 
        min_items=10,
        description="List of applications (minimum 10 for statistical validity)"
    )
    protected_attribute_name: str = Field(
        default="gender",
        description="Name of protected attribute (e.g., 'gender', 'race', 'age_group')"
    )
    privileged_groups: Optional[List[Union[str, int]]] = Field(
        None,
        description="List of privileged group values (auto-detected if not provided)"
    )
    unprivileged_groups: Optional[List[Union[str, int]]] = Field(
        None,
        description="List of unprivileged group values (auto-detected if not provided)"
    )
    favorable_label: int = Field(
        default=1,
        description="Label for favorable outcome (default: 1 = hired)"
    )
    
    @validator('applications')
    def validate_applications(cls, v):
        if len(v) < 10:
            raise ValueError('Minimum 10 applications required for statistical validity')
        return v


class GroupStatistics(BaseModel):
    """Statistics for a demographic group"""
    group_value: str
    count: int
    selected_count: int
    selection_rate: float
    true_positive_rate: Optional[float] = None
    false_positive_rate: Optional[float] = None
    true_negative_rate: Optional[float] = None
    false_negative_rate: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None


class FairnessMetrics(BaseModel):
    """AIF360-computed fairness metrics"""
    # Core Metrics
    statistical_parity_difference: float = Field(
        ..., 
        description="Demographic parity difference (ideal: 0, threshold: ±0.1)"
    )
    disparate_impact_ratio: float = Field(
        ..., 
        description="Disparate impact ratio (ideal: 1.0, legal threshold: ≥0.8)"
    )
    equal_opportunity_difference: Optional[float] = Field(
        None,
        description="True positive rate difference (ideal: 0, threshold: ±0.1)"
    )
    average_odds_difference: Optional[float] = Field(
        None,
        description="Average of TPR and FPR differences (ideal: 0)"
    )
    
    # Error Rate Metrics
    false_positive_rate_difference: Optional[float] = None
    false_negative_rate_difference: Optional[float] = None
    
    # Predictive Metrics
    predictive_parity_difference: Optional[float] = Field(
        None,
        description="Precision difference across groups (ideal: 0)"
    )
    
    # Calibration
    calibration_score: Optional[float] = Field(
        None,
        description="Calibration quality (Brier score if available)"
    )


class BiasViolation(BaseModel):
    """Detected bias violation"""
    metric: str
    value: float
    threshold: float
    severity: str  # "critical", "high", "medium", "low"
    affected_groups: List[str]
    interpretation: str


class FairnessBadge(BaseModel):
    """Fairness certification badge"""
    grade: str  # "A+", "A", "B", "C", "D", "F"
    score: float  # 0-100
    level: str  # "Excellent", "Good", "Acceptable", "Fair", "Poor", "Critical"
    color: str  # "#28a745", "#ffc107", "#dc3545"


class AnalysisResponse(BaseModel):
    """Complete fairness analysis response"""
    timestamp: str
    analysis_id: str
    
    # Summary
    total_applications: int
    bias_detected: bool
    fairness_badge: FairnessBadge
    
    # Metrics
    fairness_metrics: FairnessMetrics
    
    # Group Analysis
    group_statistics: List[GroupStatistics]
    
    # Bias Detection
    violations: List[BiasViolation]
    total_violations: int
    critical_violations: int
    
    # Recommendations
    recommendations: List[str]
    
    # Metadata
    computation_time_ms: float
    aif360_version: str


# ============================================================================
# AIF360 FAIRNESS ENGINE
# ============================================================================

class AIF360FairnessEngine:
    """
    Enterprise-grade fairness engine using IBM AIF360
    
    This class wraps AIF360's BinaryLabelDataset and ClassificationMetric
    to provide production-ready fairness analysis with comprehensive
    bias detection and actionable recommendations.
    """
    
    def __init__(self):
        if not AIF360_AVAILABLE:
            raise RuntimeError(
                "AIF360 is not installed. Install with: pip install aif360"
            )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze(
        self,
        applications: List[Application],
        protected_attribute_name: str,
        privileged_groups: Optional[List] = None,
        unprivileged_groups: Optional[List] = None,
        favorable_label: int = 1
    ) -> Dict:
        """
        Perform comprehensive fairness analysis using AIF360
        
        Args:
            applications: List of application records
            protected_attribute_name: Name of protected attribute
            privileged_groups: List of privileged group values
            unprivileged_groups: List of unprivileged group values
            favorable_label: Label for positive outcome
            
        Returns:
            Complete fairness analysis with metrics, violations, recommendations
        """
        start_time = time.time()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                protected_attribute_name: app.protected_attribute,
                'decision': app.decision,
                'ground_truth': app.ground_truth if app.ground_truth is not None else app.decision
            }
            for app in applications
        ])
        
        self.logger.info(f"Analyzing {len(df)} applications")
        
        # Auto-detect privileged/unprivileged groups
        unique_groups = df[protected_attribute_name].unique()
        if privileged_groups is None or unprivileged_groups is None:
            privileged_groups, unprivileged_groups = self._auto_detect_groups(
                df, protected_attribute_name
            )
        
        self.logger.info(f"Privileged groups: {privileged_groups}")
        self.logger.info(f"Unprivileged groups: {unprivileged_groups}")
        
        # Create AIF360 datasets
        try:
            dataset = BinaryLabelDataset(
                df=df,
                label_names=['decision'],
                protected_attribute_names=[protected_attribute_name],
                favorable_label=favorable_label,
                unfavorable_label=1 - favorable_label
            )
            
            # For classification metrics (if ground truth available)
            dataset_pred = BinaryLabelDataset(
                df=df,
                label_names=['ground_truth'],
                protected_attribute_names=[protected_attribute_name],
                favorable_label=favorable_label,
                unfavorable_label=1 - favorable_label
            )
            dataset_pred.labels = df['decision'].values.reshape(-1, 1)
            
        except Exception as e:
            self.logger.error(f"Failed to create AIF360 dataset: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data format error: {str(e)}"
            )
        
        # Compute metrics
        metrics = self._compute_fairness_metrics(
            dataset=dataset,
            dataset_pred=dataset_pred,
            privileged_groups=[{protected_attribute_name: g} for g in privileged_groups],
            unprivileged_groups=[{protected_attribute_name: g} for g in unprivileged_groups]
        )
        
        # Compute group statistics
        group_stats = self._compute_group_statistics(df, protected_attribute_name)
        
        # Detect bias violations
        violations = self._detect_violations(metrics, group_stats)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(violations, metrics)
        
        # Calculate fairness score and badge
        fairness_score = self._calculate_fairness_score(metrics)
        badge = self._get_fairness_badge(fairness_score)
        
        computation_time = (time.time() - start_time) * 1000
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_id': f"analysis_{int(time.time())}_{hash(str(applications[:5])) % 10000}",
            'total_applications': len(df),
            'bias_detected': len(violations) > 0,
            'fairness_badge': badge,
            'fairness_metrics': metrics,
            'group_statistics': group_stats,
            'violations': violations,
            'total_violations': len(violations),
            'critical_violations': sum(1 for v in violations if v['severity'] == 'critical'),
            'recommendations': recommendations,
            'computation_time_ms': round(computation_time, 2),
            'aif360_version': '0.6.1'  # Update dynamically if needed
        }
    
    def _auto_detect_groups(
        self, 
        df: pd.DataFrame, 
        protected_attr: str
    ) -> tuple:
        """
        Auto-detect privileged and unprivileged groups
        Privileged = higher selection rate group
        """
        groups = df.groupby(protected_attr)['decision'].mean().sort_values(ascending=False)
        all_groups = list(groups.index)
        
        # Highest selection rate = privileged
        privileged = [all_groups[0]]
        unprivileged = all_groups[1:]
        
        return privileged, unprivileged
    
    def _compute_fairness_metrics(
        self,
        dataset: BinaryLabelDataset,
        dataset_pred: BinaryLabelDataset,
        privileged_groups: List[Dict],
        unprivileged_groups: List[Dict]
    ) -> Dict:
        """Compute all AIF360 fairness metrics"""
        
        # Dataset-level metrics (demographic parity, disparate impact)
        dataset_metric = BinaryLabelDatasetMetric(
            dataset,
            unprivileged_groups=unprivileged_groups,
            privileged_groups=privileged_groups
        )
        
        # Classification metrics (equal opportunity, average odds, etc.)
        try:
            classification_metric = ClassificationMetric(
                dataset_pred,
                dataset,
                unprivileged_groups=unprivileged_groups,
                privileged_groups=privileged_groups
            )
            has_ground_truth = True
        except:
            classification_metric = None
            has_ground_truth = False
        
        metrics = {
            # Core metrics (always available)
            'statistical_parity_difference': round(dataset_metric.statistical_parity_difference(), 4),
            'disparate_impact_ratio': round(dataset_metric.disparate_impact(), 4),
        }
        
        # Classification metrics (require ground truth)
        if has_ground_truth and classification_metric:
            try:
                metrics.update({
                    'equal_opportunity_difference': round(classification_metric.equal_opportunity_difference(), 4),
                    'average_odds_difference': round(classification_metric.average_odds_difference(), 4),
                    'false_positive_rate_difference': round(
                        classification_metric.false_positive_rate_difference(), 4
                    ),
                    'false_negative_rate_difference': round(
                        classification_metric.false_negative_rate_difference(), 4
                    ),
                    'predictive_parity_difference': round(
                        classification_metric.positive_predictive_value() - 
                        classification_metric.negative_predictive_value(), 4
                    )
                })
            except Exception as e:
                self.logger.warning(f"Could not compute classification metrics: {e}")
        
        return metrics
    
    def _compute_group_statistics(
        self, 
        df: pd.DataFrame, 
        protected_attr: str
    ) -> List[Dict]:
        """Compute detailed statistics per demographic group"""
        
        stats = []
        
        for group_value in df[protected_attr].unique():
            group_df = df[df[protected_attr] == group_value]
            
            count = len(group_df)
            selected = (group_df['decision'] == 1).sum()
            selection_rate = selected / count if count > 0 else 0
            
            stat = {
                'group_value': str(group_value),
                'count': count,
                'selected_count': int(selected),
                'selection_rate': round(selection_rate, 4)
            }
            
            # Compute confusion matrix metrics if ground truth available
            if 'ground_truth' in group_df.columns:
                y_true = group_df['ground_truth']
                y_pred = group_df['decision']
                
                tp = ((y_true == 1) & (y_pred == 1)).sum()
                tn = ((y_true == 0) & (y_pred == 0)).sum()
                fp = ((y_true == 0) & (y_pred == 1)).sum()
                fn = ((y_true == 1) & (y_pred == 0)).sum()
                
                stat.update({
                    'true_positive_rate': round(tp / (tp + fn), 4) if (tp + fn) > 0 else None,
                    'false_positive_rate': round(fp / (fp + tn), 4) if (fp + tn) > 0 else None,
                    'true_negative_rate': round(tn / (tn + fp), 4) if (tn + fp) > 0 else None,
                    'false_negative_rate': round(fn / (fn + tp), 4) if (fn + tp) > 0 else None,
                    'precision': round(tp / (tp + fp), 4) if (tp + fp) > 0 else None,
                    'recall': round(tp / (tp + fn), 4) if (tp + fn) > 0 else None
                })
            
            stats.append(stat)
        
        return stats
    
    def _detect_violations(
        self, 
        metrics: Dict, 
        group_stats: List[Dict]
    ) -> List[Dict]:
        """Detect fairness violations based on established thresholds"""
        
        violations = []
        
        # Thresholds (research-backed and legal standards)
        THRESHOLDS = {
            'statistical_parity_difference': 0.1,  # 10% difference
            'disparate_impact_ratio': 0.8,  # EEOC 80% rule
            'equal_opportunity_difference': 0.1,
            'average_odds_difference': 0.1,
            'false_positive_rate_difference': 0.1,
            'false_negative_rate_difference': 0.1,
            'predictive_parity_difference': 0.1
        }
        
        # Check statistical parity
        spd = metrics.get('statistical_parity_difference', 0)
        if abs(spd) > THRESHOLDS['statistical_parity_difference']:
            violations.append({
                'metric': 'statistical_parity_difference',
                'value': spd,
                'threshold': THRESHOLDS['statistical_parity_difference'],
                'severity': self._classify_severity('statistical_parity_difference', abs(spd)),
                'affected_groups': [g['group_value'] for g in group_stats],
                'interpretation': f"Selection rates differ by {abs(spd):.1%} across groups (threshold: 10%)"
            })
        
        # Check disparate impact
        di = metrics.get('disparate_impact_ratio', 1.0)
        if di < THRESHOLDS['disparate_impact_ratio']:
            severity = 'critical' if di < 0.5 else ('high' if di < 0.7 else 'medium')
            violations.append({
                'metric': 'disparate_impact_ratio',
                'value': di,
                'threshold': THRESHOLDS['disparate_impact_ratio'],
                'severity': severity,
                'affected_groups': [g['group_value'] for g in group_stats],
                'interpretation': f"Disparate impact ratio of {di:.2f} violates 80% rule (EEOC standard)"
            })
        
        # Check other metrics
        for metric_name, threshold in THRESHOLDS.items():
            if metric_name in ['statistical_parity_difference', 'disparate_impact_ratio']:
                continue
            
            value = metrics.get(metric_name)
            if value is not None and abs(value) > threshold:
                violations.append({
                    'metric': metric_name,
                    'value': value,
                    'threshold': threshold,
                    'severity': self._classify_severity(metric_name, abs(value)),
                    'affected_groups': [g['group_value'] for g in group_stats],
                    'interpretation': f"{metric_name.replace('_', ' ').title()}: {abs(value):.1%} difference detected"
                })
        
        return violations
    
    def _classify_severity(self, metric: str, value: float) -> str:
        """Classify violation severity"""
        if metric == 'disparate_impact_ratio':
            if value < 0.5:
                return 'critical'
            elif value < 0.7:
                return 'high'
            else:
                return 'medium'
        else:
            if value > 0.3:
                return 'critical'
            elif value > 0.2:
                return 'high'
            elif value > 0.1:
                return 'medium'
            else:
                return 'low'
    
    def _generate_recommendations(
        self, 
        violations: List[Dict], 
        metrics: Dict
    ) -> List[str]:
        """Generate actionable recommendations based on violations"""
        
        recommendations = []
        
        if not violations:
            recommendations.append(
                "✅ No significant bias detected. Continue monitoring fairness metrics regularly."
            )
            return recommendations
        
        # Disparate impact recommendations
        if any(v['metric'] == 'disparate_impact_ratio' for v in violations):
            recommendations.extend([
                "🚨 LEGAL RISK: Disparate impact detected. This violates EEOC 80% rule.",
                "Action: Conduct adverse impact analysis and document business necessity.",
                "Consider: Implement blind resume screening to reduce demographic bias.",
                "Review: Job requirements and qualification criteria for unintentional bias."
            ])
        
        # Statistical parity recommendations
        if any(v['metric'] == 'statistical_parity_difference' for v in violations):
            recommendations.extend([
                "Selection rates differ significantly across demographic groups.",
                "Action: Audit hiring pipeline for bias at each stage (resume screening, interviews, offers).",
                "Consider: Using AIF360's Reweighing or Disparate Impact Remover for mitigation."
            ])
        
        # Equal opportunity recommendations
        if any(v['metric'] == 'equal_opportunity_difference' for v in violations):
            recommendations.extend([
                "Qualified candidates from different groups have unequal hiring chances.",
                "Action: Review interview scoring rubrics for subjectivity and bias.",
                "Consider: Structured interviews with standardized evaluation criteria."
            ])
        
        # False positive rate recommendations
        if any(v['metric'] == 'false_positive_rate_difference' for v in violations):
            recommendations.extend([
                "Different error rates across groups (false positive disparity).",
                "Action: Calibrate decision thresholds per group using AIF360 postprocessing.",
                "Consider: Equalized Odds or Calibrated Equalized Odds algorithms."
            ])
        
        # General recommendations
        recommendations.extend([
            "Monitor: Track fairness metrics over time to detect emerging bias patterns.",
            "Train: Educate hiring managers on unconscious bias and fair evaluation practices.",
            "Audit: Conduct regular third-party fairness audits for legal compliance."
        ])
        
        return recommendations[:10]  # Limit to top 10
    
    def _calculate_fairness_score(self, metrics: Dict) -> float:
        """
        Calculate overall fairness score (0-100)
        100 = perfectly fair, 0 = severe bias
        """
        penalties = 0.0
        weight_sum = 0.0
        
        # Statistical parity (weight: 0.25)
        spd = abs(metrics.get('statistical_parity_difference', 0))
        penalties += min(spd / 0.3, 1.0) * 0.25
        weight_sum += 0.25
        
        # Disparate impact (weight: 0.30)
        di = metrics.get('disparate_impact_ratio', 1.0)
        di_penalty = max(0, (0.8 - di) / 0.8) if di < 1.0 else max(0, (di - 1.2) / 0.2)
        penalties += min(di_penalty, 1.0) * 0.30
        weight_sum += 0.30
        
        # Equal opportunity (weight: 0.20)
        eo = abs(metrics.get('equal_opportunity_difference', 0))
        penalties += min(eo / 0.3, 1.0) * 0.20
        weight_sum += 0.20
        
        # Average odds (weight: 0.15)
        ao = abs(metrics.get('average_odds_difference', 0))
        penalties += min(ao / 0.3, 1.0) * 0.15
        weight_sum += 0.15
        
        # Other metrics (weight: 0.10)
        other = abs(metrics.get('predictive_parity_difference', 0))
        penalties += min(other / 0.3, 1.0) * 0.10
        weight_sum += 0.10
        
        score = max(0, 100 * (1 - penalties / weight_sum))
        return round(score, 2)
    
    def _get_fairness_badge(self, score: float) -> Dict:
        """Assign fairness badge based on score"""
        if score >= 90:
            return {
                'grade': 'A+',
                'score': score,
                'level': 'Excellent Fairness',
                'color': '#28a745'
            }
        elif score >= 80:
            return {
                'grade': 'A',
                'score': score,
                'level': 'Good Fairness',
                'color': '#5cb85c'
            }
        elif score >= 70:
            return {
                'grade': 'B',
                'score': score,
                'level': 'Acceptable Fairness',
                'color': '#f0ad4e'
            }
        elif score >= 60:
            return {
                'grade': 'C',
                'score': score,
                'level': 'Fair Concerns',
                'color': '#fd7e14'
            }
        elif score >= 50:
            return {
                'grade': 'D',
                'score': score,
                'level': 'Serious Issues',
                'color': '#dc3545'
            }
        else:
            return {
                'grade': 'F',
                'score': score,
                'level': 'Critical Bias',
                'color': '#a71d2a'
            }


# Global engine instance
fairness_engine = AIF360FairnessEngine() if AIF360_AVAILABLE else None


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "aif360_available": AIF360_AVAILABLE,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/metrics", status_code=status.HTTP_200_OK)
async def get_metrics():
    """Prometheus-style metrics endpoint"""
    return {
        "total_requests": METRICS["total_requests"],
        "failed_requests": METRICS["failed_requests"],
        "analyses_completed": METRICS["analyses_completed"],
        "avg_analysis_time_ms": (
            METRICS["total_analysis_time"] / METRICS["analyses_completed"]
            if METRICS["analyses_completed"] > 0 else 0
        ),
        "success_rate": (
            1 - (METRICS["failed_requests"] / METRICS["total_requests"])
            if METRICS["total_requests"] > 0 else 1.0
        )
    }


@app.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_fairness(request: AnalysisRequest):
    """
    Perform comprehensive fairness analysis using AIF360
    
    This endpoint computes all AIF360 fairness metrics, detects bias violations,
    and provides actionable recommendations for improving hiring fairness.
    
    **Enterprise Features:**
    - Statistical parity / Demographic parity analysis
    - Disparate impact ratio (EEOC 80% rule compliance)
    - Equal opportunity difference (qualified candidate equality)
    - Average odds difference (error rate equality)
    - False positive/negative rate analysis
    - Predictive parity (precision equality)
    - Group-level confusion matrix statistics
    - Severity-classified bias violations
    - Actionable remediation recommendations
    - Fairness badge/certification (A+ to F)
    
    **Legal Compliance:**
    - EEOC Uniform Guidelines on Employee Selection
    - EU AI Act fairness requirements
    - UK Equality Act 2010
    """
    METRICS["total_requests"] += 1
    
    if not AIF360_AVAILABLE:
        METRICS["failed_requests"] += 1
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AIF360 is not available on this server"
        )
    
    try:
        logger.info(f"Starting fairness analysis for {len(request.applications)} applications")
        
        result = fairness_engine.analyze(
            applications=request.applications,
            protected_attribute_name=request.protected_attribute_name,
            privileged_groups=request.privileged_groups,
            unprivileged_groups=request.unprivileged_groups,
            favorable_label=request.favorable_label
        )
        
        METRICS["analyses_completed"] += 1
        METRICS["total_analysis_time"] += result['computation_time_ms']
        
        logger.info(f"Analysis complete: {result['total_violations']} violations detected")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        METRICS["failed_requests"] += 1
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Enterprise Fairness Analysis API",
        "version": "2.0.0",
        "aif360_available": AIF360_AVAILABLE,
        "endpoints": {
            "analyze": "/analyze (POST)",
            "health": "/health (GET)",
            "metrics": "/metrics (GET)",
            "docs": "/docs (GET)",
            "redoc": "/redoc (GET)"
        },
        "documentation": "/docs"
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Set to True for development
        log_level="info"
    )
