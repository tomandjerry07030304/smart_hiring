"""
ScoringConfig — Single Source of Truth for All Scoring Weights
==============================================================
Gap 6 Fix: Unifies scoring weights across ranking_service.py,
matching.py, and ml_matching_service.py.

Canonical weights (v1):
    skills      = 0.35
    experience  = 0.25
    similarity  = 0.20
    education   = 0.15
    CCI         = 0.05
    ────────────────────
    Total       = 1.00

All modules MUST import weights from this file instead of
defining their own inline constants.

Usage
-----
    from config.scoring_config import ScoringConfig

    # Full 5-component weights (ranking_service.py)
    w = ScoringConfig.WEIGHTS

    # 3-component weights for simpler matchers
    w3 = ScoringConfig.weights_for('similarity', 'skills', 'cci')

Author: Smart Hiring System
Date:   February 2026
"""

from typing import Dict, List


class ScoringConfig:
    """Canonical scoring weights — single source of truth."""

    VERSION = "1.0"

    # ── Canonical 5-component weights ──────────────────────────
    WEIGHTS: Dict[str, float] = {
        "skills":       0.35,
        "experience":   0.25,
        "similarity":   0.20,
        "education":    0.15,
        "cci":          0.05,
    }

    # ── Decision thresholds (score out of 100) ─────────────────
    THRESHOLDS = {
        "strong_match":    75,
        "good_match":      60,
        "potential_match":  45,
    }

    # ── Convenience aliases for backward-compat key names ──────
    _ALIASES: Dict[str, str] = {
        "skills_match":       "skills",
        "skill_match":        "skills",
        "resume_similarity":  "similarity",
        "semantic":           "similarity",
        "semantic_score":     "similarity",
        "tfidf":              "similarity",
        "career_consistency": "cci",
        "cci_score":          "cci",
    }

    @classmethod
    def _resolve(cls, key: str) -> str:
        """Resolve an alias to canonical key."""
        return cls._ALIASES.get(key, key)

    @classmethod
    def get(cls, key: str) -> float:
        """Return weight for a canonical or aliased key.

        >>> ScoringConfig.get('skills')
        0.35
        >>> ScoringConfig.get('skills_match')      # alias
        0.35
        >>> ScoringConfig.get('resume_similarity')  # alias
        0.20
        """
        resolved = cls._resolve(key)
        if resolved not in cls.WEIGHTS:
            raise KeyError(
                f"Unknown scoring component '{key}' (resolved: '{resolved}'). "
                f"Valid keys: {list(cls.WEIGHTS.keys())}"
            )
        return cls.WEIGHTS[resolved]

    @classmethod
    def weights_for(cls, *components: str) -> Dict[str, float]:
        """Return re-normalized weights for a subset of components.

        Use this when a module only computes some components (e.g.
        similarity + skills + cci) and needs them to sum to 1.0.

        >>> ScoringConfig.weights_for('similarity', 'skills', 'cci')
        {'similarity': 0.333, 'skills': 0.583, 'cci': 0.083}
        """
        resolved = [cls._resolve(c) for c in components]
        raw = {k: cls.WEIGHTS[k] for k in resolved}
        total = sum(raw.values())
        if total == 0:
            raise ValueError("Selected components have zero total weight")
        return {k: round(v / total, 4) for k, v in raw.items()}

    @classmethod
    def weights_for_without_cci(cls, *components: str) -> Dict[str, float]:
        """Return re-normalized weights excluding CCI.

        Useful when CCI is unavailable for a candidate.

        >>> ScoringConfig.weights_for_without_cci('similarity', 'skills')
        {'similarity': 0.3636, 'skills': 0.6364}
        """
        resolved = [cls._resolve(c) for c in components if cls._resolve(c) != 'cci']
        raw = {k: cls.WEIGHTS[k] for k in resolved}
        total = sum(raw.values())
        if total == 0:
            raise ValueError("Selected components have zero total weight")
        return {k: round(v / total, 4) for k, v in raw.items()}
