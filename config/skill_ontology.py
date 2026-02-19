"""
Skill Ontology Loader — Gap 10: Single Source of Truth
=======================================================
Loads the canonical skill taxonomy from skill_ontology.json.

All modules that need skill lists, skill aliases, or category
mappings MUST import from here instead of defining inline lists.

Usage
-----
    from config.skill_ontology import SKILL_CATEGORIES, SKILL_DATABASE, SKILL_ALIASES

Exported
--------
    SKILL_CATEGORIES : dict[str, list[str]]
        Category → list of skills
    SKILL_DATABASE : set[str]
        Flat set of every skill (for fast membership checks)
    SKILL_ALIASES : dict[str, str]
        alternate_name → canonical_name
"""

import json
import pathlib
from typing import Dict, List, Set

_ONTOLOGY_PATH = pathlib.Path(__file__).parent / 'skill_ontology.json'

with open(_ONTOLOGY_PATH, 'r', encoding='utf-8') as _f:
    _DATA = json.load(_f)

SKILL_CATEGORIES: Dict[str, List[str]] = _DATA['categories']

SKILL_DATABASE: Set[str] = set()
for _skills in SKILL_CATEGORIES.values():
    SKILL_DATABASE.update(_skills)

SKILL_ALIASES: Dict[str, str] = _DATA.get('aliases', {})
