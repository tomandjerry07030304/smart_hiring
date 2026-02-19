"""
Tests for Gap 8 – Simulated demographics → real opt-in self-identification
Tests for Gap 11 – job_processor.get_database() → get_db()

Validates:
  Gap 8:
    1. PUT /candidates/self-identification endpoint exists with validation
    2. DELETE /candidates/self-identification endpoint exists
    3. dashboard_routes no longer uses random.choice for demographics
    4. audit_routes uses real demographic lookup (not just score_group)
    5. Demographics fields have opt-in consent timestamp

  Gap 11:
    6. job_processor.py calls get_db() not get_database()
    7. Database class has get_db() method
"""

import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


# ── Gap 8 Tests ───────────────────────────────────────────────────────────────

def test_self_identification_endpoint_exists():
    """candidate_routes.py should have PUT /self-identification endpoint."""
    src = _read("backend/routes/candidate_routes.py")
    assert "'/self-identification'" in src or '"/self-identification"' in src
    assert "def update_self_identification" in src


def test_self_identification_delete_endpoint():
    """candidate_routes.py should have DELETE /self-identification endpoint."""
    src = _read("backend/routes/candidate_routes.py")
    assert "def delete_self_identification" in src


def test_self_identification_validates_input():
    """Endpoint should validate gender, age_group, ethnicity values."""
    src = _read("backend/routes/candidate_routes.py")
    assert "VALID_GENDERS" in src
    assert "VALID_AGE_GROUPS" in src
    assert "VALID_ETHNICITIES" in src


def test_self_identification_stores_consent():
    """Demographics should include consent_given_at timestamp."""
    src = _read("backend/routes/candidate_routes.py")
    assert "consent_given_at" in src


def test_dashboard_no_random_demographics():
    """dashboard_routes.py must NOT use random.choice for demographics."""
    src = _read("backend/routes/dashboard_routes.py")
    # There should be no random.choice calls for gender/age/ethnicity
    assert "random.choice" not in src, (
        "dashboard_routes.py still uses random.choice for fabricated demographics"
    )


def test_dashboard_uses_real_demographics():
    """dashboard_routes get_fairness_audit should look up candidate demographics from DB."""
    src = _read("backend/routes/dashboard_routes.py")
    assert "demographics" in src
    assert "self-identification" in src.lower() or "opt-in" in src.lower()


def test_audit_routes_uses_demographics():
    """audit_routes.py should look up real demographic data, not just score_group."""
    src = _read("backend/routes/audit_routes.py")
    # Should have demographic attribute lookup
    assert "demographics" in src
    # Should still have score_group as fallback
    assert "score_group" in src


def test_audit_routes_dynamic_attributes():
    """audit_routes should determine attribute_fields dynamically from available data."""
    src = _read("backend/routes/audit_routes.py")
    assert "attribute_fields_found" in src or "attribute_fields" in src


# ── Gap 11 Tests ──────────────────────────────────────────────────────────────

def test_job_processor_uses_get_db():
    """job_processor.py should call self.db.get_db(), not self.db.get_database()."""
    src = _read("backend/workers/job_processor.py")
    assert "get_database()" not in src, (
        "job_processor.py still references get_database() which does not exist"
    )
    assert "get_db()" in src


def test_database_has_get_db_method():
    """Database class in models/database.py must have a get_db method."""
    src = _read("backend/models/database.py")
    assert "def get_db" in src


def test_job_processor_get_db_count():
    """job_processor.py should have exactly 3 get_db() calls (resume, analytics, scoring)."""
    src = _read("backend/workers/job_processor.py")
    matches = re.findall(r"self\.db\.get_db\(\)", src)
    assert len(matches) == 3, f"Expected 3 get_db() calls, found {len(matches)}"
