"""v4.1 Regression Tests - Verifies all 4 critical bug fixes"""
import sys
sys.path.insert(0, '.')

from backend.services.resume_parser_service import (
    ResumeParser, extract_skills, extract_experience_years,
    anonymize_text, _merge_date_intervals, PHONE_PATTERNS, SKILL_DATABASE
)
from datetime import datetime

print("=" * 60)
print("  v4.1 Regression Tests - 4 Critical Bug Fixes")
print("=" * 60)

p = ResumeParser()

# =========================================================
# BUG FIX #1: "Google Skill" Bug - NER must not add ORGs
# =========================================================
print("\n[FIX #1] The 'Google Skill' Bug")
text_with_orgs = """
Experience
Software Engineer at Google
Built services at Infosys using Python and React.
Used iPhone for testing iOS apps with Flutter.
"""
skills = extract_skills(text_with_orgs)
print(f"  Skills found: {skills}")

# Google, Infosys, iPhone should NOT be in skills (they're ORGs/products, not skills)
assert 'google' not in skills, "BUG: 'Google' added as skill!"
assert 'infosys' not in skills, "BUG: 'Infosys' added as skill!"
assert 'iphone' not in skills, "BUG: 'iPhone' added as skill!"
# But Python, React, Flutter SHOULD be found (they're in SKILL_DATABASE)
assert 'python' in skills, "Python should be found!"
assert 'react' in skills, "React should be found!"
assert 'flutter' in skills, "Flutter should be found!"
print("  Google/Infosys/iPhone excluded, Python/React/Flutter found: PASS")

# =========================================================
# BUG FIX #2: "Time Traveler" Bug - Overlap merging
# =========================================================
print("\n[FIX #2] The 'Time Traveler' Bug (Date Overlap)")

# Test the merge algorithm directly
from datetime import datetime as dt
intervals = [
    (dt(2020, 1, 1), dt(2022, 1, 1)),  # Job A: 2020-2022 (2 years)
    (dt(2021, 1, 1), dt(2023, 1, 1)),  # Job B: 2021-2023 (2 years, overlaps!)
]
merged = _merge_date_intervals(intervals)
print(f"  Input:  2 jobs, 2020-2022 and 2021-2023")
print(f"  Merged: {len(merged)} interval(s)")
total = sum((e - s).days / 365.25 for s, e in merged)
print(f"  Total:  {total:.1f} years (should be ~3, NOT 4)")
assert 2.9 <= total <= 3.1, f"BUG: Got {total:.1f} years instead of ~3!"
print("  Overlap correctly merged: PASS")

# Test with resume text
overlap_text = """
Experience
Senior Developer at Company A
Jan 2020 - Jan 2022

Part-time Consultant at Company B
Jan 2021 - Jan 2023
"""
exp_years = extract_experience_years(overlap_text)
print(f"  Experience from text: {exp_years} years")
assert exp_years == 3, f"BUG: Got {exp_years} instead of 3!"
print("  Text-based overlap test: PASS")

# =========================================================
# BUG FIX #3: "Lost Candidate" Bug - Indian Phone Numbers
# =========================================================
print("\n[FIX #3] The 'Lost Candidate' Bug (Indian Phone)")

indian_resume = """Raj Kumar
raj@email.com
+91 9876543210

Skills
Python, Django
"""
result = p.parse_resume(indian_resume.encode(), "test.txt")
phone = result['contact'].get('phone', '')
print(f"  Extracted phone: '{phone}'")
assert phone and '9876543210' in phone.replace(' ', ''), f"BUG: Indian phone not found! Got: '{phone}'"
print("  Indian phone number extracted: PASS")

# Also verify anonymization catches it
anon = anonymize_text(indian_resume)
assert '9876543210' not in anon, "BUG: Indian phone not anonymized!"
print("  Indian phone anonymized: PASS")

# =========================================================
# BUG FIX #4: Name Corruption Bug
# =========================================================
print("\n[FIX #4] Name Corruption Bug")
text_with_names = """John Doe
john@email.com

Experience
Studied Java programming by James Gosling methodology.
Python was created by Guido van Rossum.
"""
anon_text = anonymize_text(text_with_names)
print(f"  Anonymized (first 200 chars): {anon_text[:200]}")

# "Java" should NOT be corrupted
assert 'Java' in anon_text or 'java' in anon_text.lower(), "BUG: 'Java' got corrupted by name removal!"
# "Python" should NOT be corrupted  
assert 'Python' in anon_text or 'python' in anon_text.lower(), "BUG: 'Python' got corrupted by name removal!"
print("  'Java' and 'Python' preserved (not corrupted): PASS")

# =========================================================
# SUMMARY
# =========================================================
print("\n" + "=" * 60)
print("  ALL 4 BUG FIXES VERIFIED - v4.1 Ready")
print("=" * 60)
