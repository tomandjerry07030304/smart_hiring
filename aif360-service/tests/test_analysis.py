"""
Unit Tests for AIF360 Fairness API
Tests core functionality, edge cases, and error handling
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)


# ============================================================================
# HEALTH & METRICS TESTS
# ============================================================================

def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "aif360_available" in data


def test_metrics_endpoint():
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "success_rate" in data


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "endpoints" in data


# ============================================================================
# FAIRNESS ANALYSIS TESTS
# ============================================================================

def test_analyze_perfect_fairness():
    """Test analysis with perfectly fair data"""
    payload = {
        "applications": [
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 0, "ground_truth": 0},
            {"protected_attribute": "female", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "female", "decision": 0, "ground_truth": 0},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 0, "ground_truth": 0},
            {"protected_attribute": "female", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "female", "decision": 0, "ground_truth": 0},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "female", "decision": 1, "ground_truth": 1},
        ],
        "protected_attribute_name": "gender"
    }
    
    response = client.post("/analyze", json=payload)
    
    if response.status_code == 503:
        pytest.skip("AIF360 not available on test system")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "fairness_metrics" in data
    assert "group_statistics" in data
    assert "violations" in data
    assert "fairness_badge" in data
    
    # Perfect fairness should have no violations
    assert data["bias_detected"] == False or data["total_violations"] <= 1
    assert data["fairness_badge"]["score"] >= 80


def test_analyze_clear_bias():
    """Test analysis with obvious bias"""
    payload = {
        "applications": [
            # All males hired
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 0},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 0},
            # All females rejected
            {"protected_attribute": "female", "decision": 0, "ground_truth": 1},
            {"protected_attribute": "female", "decision": 0, "ground_truth": 1},
            {"protected_attribute": "female", "decision": 0, "ground_truth": 0},
            {"protected_attribute": "female", "decision": 0, "ground_truth": 1},
            {"protected_attribute": "female", "decision": 0, "ground_truth": 0},
        ],
        "protected_attribute_name": "gender"
    }
    
    response = client.post("/analyze", json=payload)
    
    if response.status_code == 503:
        pytest.skip("AIF360 not available on test system")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should detect bias
    assert data["bias_detected"] == True
    assert data["total_violations"] > 0
    assert data["fairness_badge"]["score"] < 60
    
    # Should have disparate impact violation
    assert any(v["metric"] == "disparate_impact_ratio" for v in data["violations"])
    
    # Should have recommendations
    assert len(data["recommendations"]) > 0


def test_analyze_80_percent_rule_boundary():
    """Test disparate impact at 80% rule boundary"""
    payload = {
        "applications": [
            # Males: 100% selection rate (5/5)
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            # Females: 79% selection rate (4/5) - just below 80%
            {"protected_attribute": "female", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "female", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "female", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "female", "decision": 0, "ground_truth": 0},
            {"protected_attribute": "female", "decision": 1, "ground_truth": 1},
        ],
        "protected_attribute_name": "gender"
    }
    
    response = client.post("/analyze", json=payload)
    
    if response.status_code == 503:
        pytest.skip("AIF360 not available on test system")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should be close to 80% threshold
    di_ratio = data["fairness_metrics"]["disparate_impact_ratio"]
    assert 0.75 <= di_ratio <= 0.85


# ============================================================================
# INPUT VALIDATION TESTS
# ============================================================================

def test_analyze_too_few_applications():
    """Test with insufficient data"""
    payload = {
        "applications": [
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "female", "decision": 0, "ground_truth": 0},
        ],  # Only 2 applications (minimum is 10)
        "protected_attribute_name": "gender"
    }
    
    response = client.post("/analyze", json=payload)
    assert response.status_code == 422  # Validation error


def test_analyze_invalid_decision():
    """Test with invalid decision values"""
    payload = {
        "applications": [
            {"protected_attribute": "male", "decision": 2, "ground_truth": 1},  # Invalid
        ] * 10,
        "protected_attribute_name": "gender"
    }
    
    response = client.post("/analyze", json=payload)
    assert response.status_code == 422


def test_analyze_missing_protected_attribute():
    """Test with missing protected attribute"""
    payload = {
        "applications": [
            {"decision": 1, "ground_truth": 1},  # Missing protected_attribute
        ] * 10,
        "protected_attribute_name": "gender"
    }
    
    response = client.post("/analyze", json=payload)
    assert response.status_code == 422


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_analyze_single_group():
    """Test with only one demographic group"""
    payload = {
        "applications": [
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 0, "ground_truth": 0},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 0, "ground_truth": 0},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 0, "ground_truth": 0},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 0, "ground_truth": 0},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
        ],
        "protected_attribute_name": "gender"
    }
    
    response = client.post("/analyze", json=payload)
    
    if response.status_code == 503:
        pytest.skip("AIF360 not available on test system")
    
    # Should handle gracefully (might return error or perfect fairness)
    assert response.status_code in [200, 400]


def test_analyze_three_groups():
    """Test with three demographic groups"""
    payload = {
        "applications": [
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 0, "ground_truth": 0},
            {"protected_attribute": "female", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "female", "decision": 0, "ground_truth": 0},
            {"protected_attribute": "non-binary", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "non-binary", "decision": 0, "ground_truth": 0},
            {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "female", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "non-binary", "decision": 1, "ground_truth": 1},
            {"protected_attribute": "male", "decision": 0, "ground_truth": 0},
        ],
        "protected_attribute_name": "gender"
    }
    
    response = client.post("/analyze", json=payload)
    
    if response.status_code == 503:
        pytest.skip("AIF360 not available on test system")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have statistics for all 3 groups
    assert len(data["group_statistics"]) == 3


def test_analyze_without_ground_truth():
    """Test with only decisions (no ground truth)"""
    payload = {
        "applications": [
            {"protected_attribute": "male", "decision": 1},
            {"protected_attribute": "male", "decision": 0},
            {"protected_attribute": "female", "decision": 1},
            {"protected_attribute": "female", "decision": 0},
            {"protected_attribute": "male", "decision": 1},
            {"protected_attribute": "male", "decision": 0},
            {"protected_attribute": "female", "decision": 1},
            {"protected_attribute": "female", "decision": 0},
            {"protected_attribute": "male", "decision": 1},
            {"protected_attribute": "female", "decision": 1},
        ],
        "protected_attribute_name": "gender"
    }
    
    response = client.post("/analyze", json=payload)
    
    if response.status_code == 503:
        pytest.skip("AIF360 not available on test system")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should still compute basic metrics
    assert "statistical_parity_difference" in data["fairness_metrics"]
    assert "disparate_impact_ratio" in data["fairness_metrics"]
    
    # Equal opportunity requires ground truth, so might be None
    assert data["fairness_metrics"].get("equal_opportunity_difference") is None or \
           isinstance(data["fairness_metrics"].get("equal_opportunity_difference"), float)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_analyze_large_dataset():
    """Test with 1000 applications"""
    applications = []
    for i in range(1000):
        applications.append({
            "protected_attribute": "male" if i % 2 == 0 else "female",
            "decision": 1 if i % 3 == 0 else 0,
            "ground_truth": 1 if i % 4 == 0 else 0
        })
    
    payload = {
        "applications": applications,
        "protected_attribute_name": "gender"
    }
    
    response = client.post("/analyze", json=payload)
    
    if response.status_code == 503:
        pytest.skip("AIF360 not available on test system")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should complete in reasonable time (< 5 seconds)
    assert data["computation_time_ms"] < 5000


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
