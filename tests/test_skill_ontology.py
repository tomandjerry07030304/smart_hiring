"""
Tests for Gap 10 – Unified skill_ontology.json
Validates:
  1. JSON loads successfully with expected structure
  2. All 3 consumer files import from config.skill_ontology
  3. Skill counts are consistent across consumers
  4. Alias resolution works
  5. No inline SKILLS_MASTER / SKILL_CATEGORIES remain in consumers
"""

import json, os, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# ── 1. JSON integrity ─────────────────────────────────────────────────────────

def test_json_loads():
    """skill_ontology.json should load and contain categories dict."""
    path = ROOT / "config" / "skill_ontology.json"
    assert path.exists(), "skill_ontology.json missing"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "categories" in data
    assert isinstance(data["categories"], dict)
    assert len(data["categories"]) >= 10, f"Expected ≥10 categories, got {len(data['categories'])}"


def test_json_categories_structure():
    """Each category must be a non-empty list of skill strings."""
    path = ROOT / "config" / "skill_ontology.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for cat_name, skills in data["categories"].items():
        assert isinstance(skills, list), f"'{cat_name}' must be a list"
        assert len(skills) > 0, f"'{cat_name}' has empty skills list"
        for s in skills:
            assert isinstance(s, str), f"'{cat_name}' contains non-string: {s}"
    # aliases is a separate top-level key
    assert "aliases" in data, "Top-level 'aliases' key missing"
    assert isinstance(data["aliases"], dict)


def test_json_total_skill_count():
    """Unified ontology should have ≥300 unique skills."""
    path = ROOT / "config" / "skill_ontology.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_skills = set()
    for skills_list in data["categories"].values():
        all_skills.update(skills_list)
    assert len(all_skills) >= 300, f"Expected ≥300 skills, got {len(all_skills)}"


# ── 2. Python loader ──────────────────────────────────────────────────────────

def test_loader_exports():
    """config.skill_ontology should export SKILL_CATEGORIES, SKILL_DATABASE, SKILL_ALIASES."""
    from config.skill_ontology import SKILL_CATEGORIES, SKILL_DATABASE, SKILL_ALIASES
    assert isinstance(SKILL_CATEGORIES, dict)
    assert isinstance(SKILL_DATABASE, set)
    assert isinstance(SKILL_ALIASES, dict)
    assert len(SKILL_DATABASE) >= 300


def test_alias_resolution():
    """Aliases should map to canonical skills in SKILL_DATABASE."""
    from config.skill_ontology import SKILL_DATABASE, SKILL_ALIASES
    for alias, canonical in SKILL_ALIASES.items():
        assert canonical in SKILL_DATABASE, (
            f"Alias '{alias}' → '{canonical}' but canonical not in SKILL_DATABASE"
        )


# ── 3. Consumer files import from ontology ────────────────────────────────────

def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_ml_matching_imports_ontology():
    """ml_matching_service.py should import from config.skill_ontology."""
    src = _read("backend/services/ml_matching_service.py")
    assert "from config.skill_ontology import" in src or "import config.skill_ontology" in src


def test_matching_imports_ontology():
    """matching.py should import from config.skill_ontology."""
    src = _read("backend/utils/matching.py")
    assert "from config.skill_ontology import" in src or "import config.skill_ontology" in src


def test_resume_parser_imports_ontology():
    """resume_parser_service.py should import from config.skill_ontology."""
    src = _read("backend/services/resume_parser_service.py")
    assert "from config.skill_ontology import" in src or "import config.skill_ontology" in src


# ── 4. No large inline skill dicts remain ─────────────────────────────────────

def test_no_inline_skills_master_in_matching():
    """matching.py should NOT have a large inline SKILLS_MASTER list."""
    src = _read("backend/utils/matching.py")
    # A large inline block would have dozens of quoted strings in SKILLS_MASTER assignment
    match = re.search(r"SKILLS_MASTER\s*=\s*\[", src)
    if match:
        # If there's a bracketed list, it should be very short (< 50 chars) or absent
        block = src[match.start():match.start() + 200]
        quoted = re.findall(r"'[^']+?'", block)
        assert len(quoted) < 5, "matching.py still has large inline SKILLS_MASTER list"


def test_no_inline_skill_categories_in_parser():
    """resume_parser_service.py should NOT have a large inline SKILL_CATEGORIES dict."""
    src = _read("backend/services/resume_parser_service.py")
    # Look for 'programming': [ pattern which indicates the old inline dict
    hits = re.findall(r"'programming'\s*:\s*\[", src)
    assert len(hits) == 0, "resume_parser_service.py still has inline SKILL_CATEGORIES dict"


def test_no_inline_skills_master_in_ml_matching():
    """ml_matching_service.py should NOT have a large inline SKILLS_MASTER list."""
    src = _read("backend/services/ml_matching_service.py")
    match = re.search(r"SKILLS_MASTER\s*=\s*\[", src)
    if match:
        block = src[match.start():match.start() + 200]
        quoted = re.findall(r"'[^']+?'", block)
        assert len(quoted) < 5, "ml_matching_service.py still has large inline SKILLS_MASTER list"


# ── 5. Consistency: all consumers see the same skill set ───────────────────────

def test_skill_counts_consistent():
    """SKILL_DATABASE set from loader should match JSON derived set exactly."""
    from config.skill_ontology import SKILL_DATABASE, SKILL_CATEGORIES
    path = ROOT / "config" / "skill_ontology.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    json_skills = set()
    for skills_list in data["categories"].values():
        json_skills.update(skills_list)
    assert SKILL_DATABASE == json_skills, (
        f"SKILL_DATABASE ({len(SKILL_DATABASE)}) ≠ JSON skills ({len(json_skills)})"
    )
    # Also verify categories keys match
    assert set(SKILL_CATEGORIES.keys()) == set(data["categories"].keys())
