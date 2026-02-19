"""Smoke test for Resume Parser v4.0 - Entrepreneur Edition"""
import sys
sys.path.insert(0, '.')

from backend.services.resume_parser_service import (
    ResumeParser, extract_experience_years, anonymize_text,
    detect_sections, extract_skills_context_aware, SKILL_DATABASE,
    PDFPLUMBER_AVAILABLE, DATEPARSER_AVAILABLE
)

print("=" * 60)
print("  Resume Parser v4.0 - Entrepreneur Edition Smoke Test")
print("=" * 60)

# 1. Verify dependencies
print(f"\n[1] Skills in DB: {len(SKILL_DATABASE)}")
assert len(SKILL_DATABASE) >= 350, f"Expected 350+ skills, got {len(SKILL_DATABASE)}"
print(f"    pdfplumber: {PDFPLUMBER_AVAILABLE}")
print(f"    dateparser: {DATEPARSER_AVAILABLE}")
assert PDFPLUMBER_AVAILABLE, "pdfplumber not available!"
assert DATEPARSER_AVAILABLE, "dateparser not available!"
print("    PASS")

# 2. Test sample resume
sample = """John Doe
john.doe@gmail.com | +91 9876543210
Date of Birth: 15/06/1995 | Nationality: Indian | Marital Status: Single

Summary
Experienced software developer with 5+ years of expertise in Python and cloud.

Skills
Python, React, Docker, AWS, Machine Learning, Kubernetes, PostgreSQL

Experience
Senior Software Engineer at Google
Jan 2020 - Present
Built microservices with Python and Docker.

Junior Developer at Startup
Mar 2018 - Dec 2019
Developed web apps using React and Node.js.

Projects
Smart Hiring Platform (Python, Flask, React)
An AI-powered hiring system with bias-free screening.

Education
B.Tech in Computer Science, MIT 2018

Languages
English - Fluent
Hindi - Native

Hobbies
Playing chess and Python scripting for fun
"""

p = ResumeParser()
result = p.parse_resume(sample.encode(), "test.txt")

# 3. Verify v4.0 output structure
print(f"\n[2] Parser version: {result.get('parser_version')}")
assert result['parser_version'] == '4.0', "Wrong version!"
print("    PASS")

# 4. Skills
skill_count = len(result['skills'])
ca_count = len(result['skills_context_aware'])
print(f"\n[3] Skills (categorized): {skill_count}")
print(f"    Skills (context-aware): {ca_count}")
assert skill_count > 0, "No skills found!"
assert ca_count > 0, "No context-aware skills found!"
print("    PASS")

# 5. Context-aware filtering: Python in hobbies should be excluded
ca_sections = [s['section'] for s in result['skills_context_aware']]
print(f"\n[4] Context-aware sections: {set(ca_sections)}")
assert 'interests' not in ca_sections, "Skills from hobbies leaked through!"
print("    Skills from HOBBIES correctly excluded: PASS")

# 6. Experience with dateparser
exp_years = result['experience']['total_years']
print(f"\n[5] Experience years: {exp_years}")
assert exp_years >= 5, f"Expected >= 5 years, got {exp_years}"
print("    PASS")

# 7. Projects
projects = result['projects']
print(f"\n[6] Projects found: {len(projects)}")
if projects:
    print(f"    First project: {projects[0]['name']}")
    print(f"    Tech stack: {projects[0]['tech_stack']}")
assert len(projects) > 0, "No projects found!"
print("    PASS")

# 8. Languages
languages = result['languages']
print(f"\n[7] Languages found: {len(languages)}")
for lang in languages:
    print(f"    {lang['language']}: {lang['proficiency']}")
assert len(languages) > 0, "No languages found!"
print("    PASS")

# 9. Sections detected
sections = list(result['sections'].keys())
print(f"\n[8] Sections detected: {sections}")
assert 'skills' in sections, "Skills section not detected!"
assert 'experience' in sections, "Experience section not detected!"
print("    PASS")

# 10. Confidence scores
conf = result['confidence']
print(f"\n[9] Confidence scores:")
for k, v in conf.items():
    print(f"    {k}: {v}")
assert 'overall' in conf, "No overall confidence!"
assert conf['overall'] > 0, "Zero confidence!"
print("    PASS")

# 11. Anonymization - check DOB, nationality, marital removal
anon = result['anonymized_text']
print(f"\n[10] Anonymization checks:")
assert 'john.doe@gmail.com' not in anon, "Email not removed!"
print("     Email removed: PASS")
assert '9876543210' not in anon, "Phone not removed!"
print("     Phone removed: PASS")
assert 'Indian' not in anon, "Nationality not removed!"
print("     Nationality removed: PASS")
assert 'Single' not in anon.split(), "Marital status not removed!"
print("     Marital status removed: PASS")

# 12. Backward compatibility
print(f"\n[11] Backward compatibility:")
assert 'raw_text' in result, "raw_text missing!"
assert 'skills' in result, "skills missing!"
assert 'experience' in result, "experience missing!"
assert 'education' in result, "education missing!"
assert 'certifications' in result, "certifications missing!"
assert 'summary' in result, "summary missing!"
assert 'anonymized_text' in result, "anonymized_text missing!"
assert 'contact' in result, "contact missing!"
assert 'metadata' in result, "metadata missing!"
print("     All v3.0 fields present: PASS")

# New fields
assert 'skills_context_aware' in result, "skills_context_aware missing!"
assert 'projects' in result, "projects missing!"
assert 'languages' in result, "languages missing!"
assert 'confidence' in result, "confidence missing!"
assert 'sections' in result, "sections missing!"
print("     All v4.0 fields present: PASS")

print("\n" + "=" * 60)
print("  ALL 11 TESTS PASSED - v4.0 Entrepreneur Edition VERIFIED")
print("=" * 60)
