"""Quick test to verify the fuzzy skill matching fix."""
import sys
sys.path.insert(0, '.')

from backend.services.ml_matching_service import MLMatchingService

svc = MLMatchingService()

print("=" * 60)
print("SKILL MATCHING FIX VERIFICATION")
print("=" * 60)

# Test 1: Data Scientist - simulating the real job
print("\n--- TEST 1: Data Scientist Job ---")
r = svc.compute_skill_match(
    job_skills=['python', 'machine learning', 'pandas', 'numpy', 'scikit-learn'],
    candidate_skills=['python', 'ml', 'data analysis', 'pandas', 'numpy', 'sklearn', 'tensorflow']
)
pct = r['score'] * 100
print(f"  Skill Score: {pct:.0f}%")
print(f"  Matched:     {r['matched_skills']}")
print(f"  Missing:     {r['missing_skills']}")

# Test 2: Frontend React Developer
print("\n--- TEST 2: Frontend React Developer ---")
r2 = svc.compute_skill_match(
    job_skills=['react', 'javascript', 'typescript', 'html', 'css'],
    candidate_skills=['reactjs', 'js', 'ts', 'html5', 'css3', 'redux']
)
pct2 = r2['score'] * 100
print(f"  Skill Score: {pct2:.0f}%")
print(f"  Matched:     {r2['matched_skills']}")
print(f"  Missing:     {r2['missing_skills']}")

# Test 3: Senior Python Developer
print("\n--- TEST 3: Senior Python Developer ---")
r3 = svc.compute_skill_match(
    job_skills=['python', 'django', 'rest api', 'postgresql', 'docker'],
    candidate_skills=['python', 'django', 'restful api', 'postgres', 'docker', 'kubernetes']
)
pct3 = r3['score'] * 100
print(f"  Skill Score: {pct3:.0f}%")
print(f"  Matched:     {r3['matched_skills']}")
print(f"  Missing:     {r3['missing_skills']}")

# Test 4: OLD behavior simulation (no aliases)
print("\n--- COMPARISON: Old exact-match behavior ---")
old_job = set(s.lower() for s in ['python', 'machine learning', 'pandas', 'numpy', 'scikit-learn'])
old_cand = set(s.lower() for s in ['python', 'ml', 'data analysis', 'pandas', 'numpy', 'sklearn', 'tensorflow'])
old_matched = old_job & old_cand
old_score = len(old_matched) / len(old_job) * 100
print(f"  Old Score: {old_score:.0f}%  (matched: {old_matched})")
print(f"  New Score: {pct:.0f}%  (matched: {r['matched_skills']})")

print("\n" + "=" * 60)
print("DONE - Scores should be significantly higher now!")
print("=" * 60)
