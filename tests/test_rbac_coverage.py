"""
Test RBAC Decorator Coverage — Gap 5
=====================================
Verifies that all protected routes have proper RBAC decorators
(require_permission, require_role, or require_any_permission)
beyond just @jwt_required().
"""

import sys, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ROUTES_DIR = ROOT / 'backend' / 'routes'

# Routes expected to have RBAC decorators (file → min count of RBAC-decorated routes)
EXPECTED_RBAC = {
    'admin_routes.py': 3,
    'audit_routes.py': 5,
    'company_routes.py': 4,
    'dashboard_routes.py': 3,
    'webhook_routes.py': 7,
    'ai_interview_routes.py': 6,
    'assessment_routes.py': 9,
    'candidate_routes.py': 5,
    'job_routes.py': 6,  # 6 of 8 routes are protected (2 are public)
}

# Files that are intentionally RBAC-exempt (public auth/oauth flows)
EXEMPT_FILES = {
    'auth_routes.py',        # public login/register
    'google_oauth_routes.py',  # OAuth callbacks
    'email_preferences_routes.py',  # unsubscribe is public
    'ai_interview_routes_v2.py',  # linkedin callback is public
}

RBAC_PATTERN = re.compile(
    r'@require_permission\(|@require_role\(|@require_any_permission\(',
    re.MULTILINE
)

ROUTE_PATTERN = re.compile(
    r'@\w+\.route\(',
    re.MULTILINE
)


def test_rbac_import_present():
    """Each non-exempt route file must import from backend.security.rbac."""
    for fname, _ in EXPECTED_RBAC.items():
        fpath = ROUTES_DIR / fname
        assert fpath.exists(), f"{fname} not found"
        src = fpath.read_text(encoding='utf-8')
        assert 'from backend.security.rbac import' in src, \
            f"{fname} missing RBAC import"


def test_rbac_decorator_count():
    """Each non-exempt route file must have at least N RBAC decorators."""
    for fname, min_count in EXPECTED_RBAC.items():
        fpath = ROUTES_DIR / fname
        src = fpath.read_text(encoding='utf-8')
        found = len(RBAC_PATTERN.findall(src))
        assert found >= min_count, (
            f"{fname}: expected >= {min_count} RBAC decorators, found {found}"
        )


def test_no_jwt_only_routes_in_critical_files():
    """
    In critical files (admin, audit, company), every @jwt_required()
    MUST be followed by an RBAC decorator before the next def.
    """
    critical = ['admin_routes.py', 'audit_routes.py', 'company_routes.py']
    for fname in critical:
        fpath = ROUTES_DIR / fname
        src = fpath.read_text(encoding='utf-8')
        lines = src.splitlines()
        
        for i, line in enumerate(lines):
            if '@jwt_required()' in line:
                # Next non-blank, non-comment line should have RBAC decorator
                for j in range(i + 1, min(i + 3, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('def '):
                        # Found function def without RBAC decorator between
                        assert False, (
                            f"{fname} L{i+1}: @jwt_required() not followed "
                            f"by RBAC decorator before def at L{j+1}"
                        )
                    if RBAC_PATTERN.search(next_line):
                        break  # Good — RBAC decorator found


def test_total_rbac_coverage():
    """At least 48 of the ~67 protected routes should have RBAC."""
    total_rbac = 0
    for py_file in ROUTES_DIR.glob('*.py'):
        if py_file.name.startswith('__'):
            continue
        src = py_file.read_text(encoding='utf-8')
        total_rbac += len(RBAC_PATTERN.findall(src))
    
    # 48 = admin(3) + audit(5) + company(4) + dashboard(3) +
    #       webhook(7) + ai_interview(6) + assessment(9) +
    #       candidate(5) + job(6) + dsr_existing(2)
    assert total_rbac >= 48, f"Total RBAC decorators = {total_rbac}, expected >= 48"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
