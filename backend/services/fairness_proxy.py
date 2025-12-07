"""
Dual-Engine Fairness Proxy with Automatic Failover
===================================================
Enterprise-grade fairness evaluation with primary/fallback architecture

Architecture:
- Primary: AIF360 Microservice (advanced fairness analysis)
- Fallback: Lightweight Fairness Engine (always active, reliable)

Failover Strategy:
- Attempt AIF360 microservice first (timeout: 5s)
- On failure/timeout → automatic seamless fallback to lightweight engine
- No user impact, logged for monitoring

Author: Smart Hiring System Team
Date: December 2025
"""

import logging
import requests
from typing import Dict, List, Optional, Any
import numpy as np
from datetime import datetime
import os

from backend.services.fairness_engine import FairnessMetrics

logger = logging.getLogger(__name__)


class FairnessProxy:
    """
    Enterprise fairness evaluation proxy with dual-engine support
    
    Primary: AIF360 Microservice (full capabilities)
    Fallback: Lightweight Engine (guaranteed availability)
    """
    
    def __init__(self):
        """Initialize fairness proxy with configuration"""
        self.aif360_url = os.getenv('AIF360_SERVICE_URL', None)
        self.aif360_enabled = bool(self.aif360_url)
        self.timeout = 5  # seconds
        self.max_retries = 2
        
        # Health tracking
        self.aif360_failures = 0
        self.aif360_successes = 0
        self.fallback_uses = 0
        
        self._log_initialization()
    
    def _log_initialization(self):
        """Log initialization status"""
        if self.aif360_enabled:
            logger.info(f"✅ Dual-engine fairness proxy initialized")
            logger.info(f"   Primary: AIF360 Microservice at {self.aif360_url}")
            logger.info(f"   Fallback: Lightweight Engine (always active)")
        else:
            logger.info(f"✅ Single-engine fairness proxy initialized")
            logger.info(f"   Engine: Lightweight Fairness Engine")
            logger.warning(f"   AIF360_SERVICE_URL not set - microservice disabled")
    
    def evaluate_fairness(
        self,
        predictions: List[int],
        labels: List[int],
        sensitive_features: List[str],
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate fairness with automatic failover
        
        Args:
            predictions: Binary predictions [0, 1, 1, 0, ...]
            labels: Ground truth labels [0, 1, 0, 1, ...]
            sensitive_features: Protected attributes ['Male', 'Female', ...]
            feature_names: Optional feature names
        
        Returns:
            Comprehensive fairness evaluation results
        """
        # Try AIF360 microservice first (if enabled)
        if self.aif360_enabled:
            try:
                result = self._call_aif360_service(
                    predictions, labels, sensitive_features, feature_names
                )
                if result:
                    self.aif360_successes += 1
                    logger.info(f"✅ AIF360 microservice evaluation successful")
                    return self._enrich_result(result, engine='aif360')
            except Exception as e:
                self.aif360_failures += 1
                logger.warning(
                    f"⚠️ AIF360 microservice failed (attempt {self.aif360_failures}): {e}"
                )
                logger.info(f"🔄 Automatic failover to lightweight engine...")
        
        # Fallback to lightweight engine
        self.fallback_uses += 1
        result = self._call_lightweight_engine(
            predictions, labels, sensitive_features
        )
        logger.info(f"✅ Lightweight engine evaluation successful (fallback use #{self.fallback_uses})")
        return self._enrich_result(result, engine='lightweight')
    
    def _call_aif360_service(
        self,
        predictions: List[int],
        labels: List[int],
        sensitive_features: List[str],
        feature_names: Optional[List[str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Call AIF360 microservice with retry logic
        
        Returns:
            Fairness evaluation results or None on failure
        """
        payload = {
            'predictions': predictions,
            'labels': labels,
            'sensitive_features': sensitive_features,
            'feature_names': feature_names or []
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.aif360_url}/api/fairness/evaluate",
                    json=payload,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(
                        f"AIF360 service returned status {response.status_code}: {response.text}"
                    )
            except requests.exceptions.Timeout:
                logger.warning(f"AIF360 service timeout (attempt {attempt + 1}/{self.max_retries})")
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"AIF360 service connection error: {e}")
            except Exception as e:
                logger.error(f"AIF360 service unexpected error: {e}")
        
        return None
    
    def _call_lightweight_engine(
        self,
        predictions: List[int],
        labels: List[int],
        sensitive_features: List[str]
    ) -> Dict[str, Any]:
        """
        Call lightweight fairness engine (guaranteed to work)
        
        Returns:
            Fairness evaluation results
        """
        # Convert to numpy arrays
        preds = np.array(predictions)
        labs = np.array(labels)
        sens = np.array(sensitive_features)
        
        # Initialize fairness calculator
        calculator = FairnessMetrics(
            predictions=preds,
            labels=labs,
            sensitive_features=sens,
            favorable_label=1
        )
        
        # Compute all fairness metrics
        results = {
            'demographic_parity': calculator.demographic_parity_difference(),
            'disparate_impact': calculator.disparate_impact(),
            'equal_opportunity': calculator.equal_opportunity_difference(),
            'equalized_odds': calculator.equalized_odds_difference(),
            'predictive_parity': calculator.predictive_parity_difference(),
            'group_metrics': calculator.group_fairness_metrics(),
            'overall_fairness_score': calculator.overall_fairness_score(),
            'is_fair': calculator.is_fair(
                dp_threshold=0.1,
                di_threshold=0.8,
                eo_threshold=0.1
            )
        }
        
        return results
    
    def _enrich_result(self, result: Dict[str, Any], engine: str) -> Dict[str, Any]:
        """
        Enrich results with metadata
        
        Args:
            result: Raw fairness evaluation results
            engine: Engine used ('aif360' or 'lightweight')
        
        Returns:
            Enriched results with metadata
        """
        result['_metadata'] = {
            'engine': engine,
            'timestamp': datetime.utcnow().isoformat(),
            'aif360_enabled': self.aif360_enabled,
            'aif360_url': self.aif360_url if self.aif360_enabled else None,
            'statistics': {
                'aif360_successes': self.aif360_successes,
                'aif360_failures': self.aif360_failures,
                'fallback_uses': self.fallback_uses
            }
        }
        return result
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check health of fairness engines
        
        Returns:
            Health status of both engines
        """
        health = {
            'lightweight_engine': {
                'status': 'healthy',
                'available': True,
                'uses': self.fallback_uses
            }
        }
        
        if self.aif360_enabled:
            # Try pinging AIF360 service
            try:
                response = requests.get(
                    f"{self.aif360_url}/health",
                    timeout=3
                )
                aif360_healthy = response.status_code == 200
            except:
                aif360_healthy = False
            
            health['aif360_microservice'] = {
                'status': 'healthy' if aif360_healthy else 'unhealthy',
                'available': aif360_healthy,
                'url': self.aif360_url,
                'successes': self.aif360_successes,
                'failures': self.aif360_failures
            }
        else:
            health['aif360_microservice'] = {
                'status': 'disabled',
                'available': False,
                'reason': 'AIF360_SERVICE_URL not configured'
            }
        
        return health
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics"""
        total_evaluations = self.aif360_successes + self.fallback_uses
        
        return {
            'total_evaluations': total_evaluations,
            'aif360_successes': self.aif360_successes,
            'aif360_failures': self.aif360_failures,
            'fallback_uses': self.fallback_uses,
            'aif360_success_rate': (
                self.aif360_successes / total_evaluations * 100 
                if total_evaluations > 0 else 0
            ),
            'fallback_rate': (
                self.fallback_uses / total_evaluations * 100
                if total_evaluations > 0 else 0
            )
        }


# Global singleton instance
_fairness_proxy = None


def get_fairness_proxy() -> FairnessProxy:
    """
    Get global fairness proxy instance (singleton)
    
    Returns:
        Initialized FairnessProxy instance
    """
    global _fairness_proxy
    if _fairness_proxy is None:
        _fairness_proxy = FairnessProxy()
    return _fairness_proxy
