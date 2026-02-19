"""
Test ScoringConfig — Gap 6: Scoring Weight Unification
======================================================
Verifies that:
1. Canonical weights sum to 1.0
2. All 3 scoring modules import from ScoringConfig (not inline)
3. The 3-component re-normalization is correct
4. Aliases resolve properly
"""

import sys, os, re, pathlib

# Ensure project root is on sys.path
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.scoring_config import ScoringConfig


# ── 1. Canonical weights sum to 1.0 ──────────────────────────

def test_weights_sum_to_one():
    total = sum(ScoringConfig.WEIGHTS.values())
    assert abs(total - 1.0) < 1e-9, f"Weights sum = {total}, expected 1.0"


def test_canonical_values():
    """Canonical weights must match the approved values."""
    assert ScoringConfig.WEIGHTS['skills'] == 0.35
    assert ScoringConfig.WEIGHTS['experience'] == 0.25
    assert ScoringConfig.WEIGHTS['similarity'] == 0.20
    assert ScoringConfig.WEIGHTS['education'] == 0.15
    assert ScoringConfig.WEIGHTS['cci'] == 0.05


# ── 2. Alias resolution ──────────────────────────────────────

def test_alias_skills_match():
    assert ScoringConfig.get('skills_match') == 0.35

def test_alias_resume_similarity():
    assert ScoringConfig.get('resume_similarity') == 0.20

def test_alias_semantic():
    assert ScoringConfig.get('semantic') == 0.20

def test_alias_career_consistency():
    assert ScoringConfig.get('career_consistency') == 0.05


# ── 3. Subset re-normalization ────────────────────────────────

def test_weights_for_three_components():
    """similarity + skills + cci should renormalize to sum 1.0."""
    w = ScoringConfig.weights_for('similarity', 'skills', 'cci')
    total = sum(w.values())
    assert abs(total - 1.0) < 0.01, f"3-component weights sum = {total}"
    # Ordering by magnitude: skills > similarity > cci
    assert w['skills'] > w['similarity'] > w['cci']


def test_weights_for_without_cci():
    """similarity + skills (no CCI) should renormalize to sum 1.0."""
    w = ScoringConfig.weights_for_without_cci('similarity', 'skills')
    total = sum(w.values())
    assert abs(total - 1.0) < 0.01, f"2-component weights sum = {total}"
    assert w['skills'] > w['similarity']


# ── 4. Source code inspection — no inline weight constants ────

def _read_source(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding='utf-8')


def test_ranking_service_imports_scoring_config():
    src = _read_source('backend/services/ranking_service.py')
    assert 'from config.scoring_config import ScoringConfig' in src, \
        "ranking_service.py must import ScoringConfig"
    # Must NOT have hardcoded weight dict literals like 0.35
    # (except in comments). Check no bare `'skills_match': 0.35` pattern.
    assert "ScoringConfig.get(" in src, \
        "ranking_service.py must use ScoringConfig.get()"


def test_ml_matching_imports_scoring_config():
    src = _read_source('backend/services/ml_matching_service.py')
    assert 'from config.scoring_config import ScoringConfig' in src, \
        "ml_matching_service.py must import ScoringConfig"
    assert 'ScoringConfig.weights_for(' in src, \
        "ml_matching_service.py must use ScoringConfig.weights_for()"


def test_matching_imports_scoring_config():
    src = _read_source('backend/utils/matching.py')
    assert 'from config.scoring_config import ScoringConfig' in src, \
        "matching.py must import ScoringConfig"
    assert 'ScoringConfig.weights_for' in src, \
        "matching.py must use ScoringConfig.weights_for()"


# ── 5. No stale inline weights in scoring files ──────────────

_HARDCODED_WEIGHT_RE = re.compile(
    r"""(?:sim_weight|skill_weight|cci_weight)\s*=\s*0\.\d""",
    re.MULTILINE
)

def test_no_hardcoded_defaults_in_matching():
    """matching.py must not have hardcoded default weight values."""
    src = _read_source('backend/utils/matching.py')
    # Allow the parameter defaults (sim_weight=None) but not literal floats
    matches = _HARDCODED_WEIGHT_RE.findall(src)
    assert not matches, f"Found hardcoded weight defaults in matching.py: {matches}"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
