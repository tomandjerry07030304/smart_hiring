"""
Test SSRF Protection — Gap 7
=============================
Verifies that resume_tasks.validate_url_ssrf blocks
internal/private network URLs while allowing valid public URLs.
"""

import sys, pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.tasks.resume_tasks import validate_url_ssrf


# ── Should BLOCK ─────────────────────────────────────────────

@pytest.mark.parametrize("url", [
    "http://127.0.0.1/admin",
    "http://localhost/secrets",
    "http://169.254.169.254/latest/meta-data/",   # AWS metadata
    "http://10.0.0.1/internal",
    "http://192.168.1.1/router",
    "http://172.16.0.1/service",
    "ftp://example.com/file.pdf",                  # wrong scheme
    "file:///etc/passwd",                          # local file
    "gopher://evil.com",                           # exotic scheme
])
def test_block_internal_urls(url):
    with pytest.raises(ValueError):
        validate_url_ssrf(url)


# ── Should ALLOW ─────────────────────────────────────────────

@pytest.mark.parametrize("url", [
    "https://storage.googleapis.com/bucket/resume.pdf",
    "https://s3.amazonaws.com/bucket/resume.pdf",
    "https://example.com/uploads/resume.pdf",
])
def test_allow_public_urls(url):
    # Should not raise
    result = validate_url_ssrf(url)
    assert result == url


# ── Source code inspection ────────────────────────────────────

def test_resume_tasks_uses_validation():
    src = (ROOT / 'backend' / 'tasks' / 'resume_tasks.py').read_text(encoding='utf-8')
    assert 'validate_url_ssrf' in src, "resume_tasks.py must call validate_url_ssrf"
    assert 'allow_redirects=False' in src, "requests.get must disable redirects"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
