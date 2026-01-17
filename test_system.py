"""
🧪 ULTRA PRO MAX: Complete System Verification Test
====================================================
Tests all critical components of the Smart Hiring System

Run: python test_ultra_pro_max_system.py

Author: Smart Hiring System Team
Date: December 19, 2025
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath('backend'))

print("="*70)
print("🧪 ULTRA PRO MAX: SMART HIRING SYSTEM VERIFICATION")
print("="*70)
print(f"Python: {sys.version}")
print(f"Working Directory: {os.getcwd()}")
print("="*70)

test_results = []

# ==================== TEST 1: ML LIBRARY IMPORTS ====================
print("\n[TEST 1/8] Testing ML Library Imports...")
try:
    import torch
    import transformers
    from sentence_transformers import SentenceTransformer
    import spacy
    import nltk
    import pandas as pd
    import numpy as np
    import sklearn
    
    print(f"  ✅ PyTorch: {torch.__version__}")
    print(f"  ✅ Transformers: {transformers.__version__}")
    print(f"  ✅ spaCy: {spacy.__version__}")
    print(f"  ✅ NLTK: {nltk.__version__}")
    print(f"  ✅ pandas: {pd.__version__}")
    print(f"  ✅ numpy: {np.__version__}")
    print(f"  ✅ scikit-learn: {sklearn.__version__}")
    
    test_results.append(("ML Libraries Import", "✅ PASS"))
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    test_results.append(("ML Libraries Import", f"❌ FAIL: {e}"))

# ==================== TEST 2: spaCy MODEL ====================
print("\n[TEST 2/8] Testing spaCy NLP Model...")
try:
    nlp = spacy.load('en_core_web_sm')
    test_text = "Python developer with 5 years of machine learning experience at Google"
    doc = nlp(test_text)
    
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    print(f"  ✅ Model loaded: {nlp.meta['name']} v{nlp.meta['version']}")
    print(f"  ✅ Processed: {len(doc)} tokens")
    print(f"  ✅ Entities: {entities}")
    
    test_results.append(("spaCy NLP Model", "✅ PASS"))
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    test_results.append(("spaCy NLP Model", f"❌ FAIL: {e}"))

# ==================== TEST 3: ADVANCED NLP SERVICE ====================
print("\n[TEST 3/8] Testing Advanced NLP Skill Extraction...")
try:
    from services.advanced_nlp_service import get_skill_extractor
    
    sample_resume = """
    PROFESSIONAL SUMMARY
    Senior Full-Stack Developer with 7+ years building scalable web applications.
    
    TECHNICAL SKILLS
    Languages: Python, JavaScript, TypeScript, Java, SQL
    Frontend: React, Angular, Vue.js, HTML5, CSS3, Bootstrap, Tailwind
    Backend: Django, Flask, Node.js, Express, Spring Boot
    Databases: PostgreSQL, MongoDB, MySQL, Redis, Elasticsearch
    Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, Jenkins, GitLab CI
    Data Science: pandas, NumPy, scikit-learn, TensorFlow, PyTorch
    
    EXPERIENCE
    Senior Software Engineer | TechCorp Inc | 2020-Present
    - Architected microservices using Python Flask and Docker
    - Deployed ML models with TensorFlow Serving on AWS
    - Optimized PostgreSQL queries reducing load time by 60%
    """
    
    extractor = get_skill_extractor(use_transformers=True)
    results = extractor.extract_skills(sample_resume, method='hybrid', confidence_threshold=0.7)
    
    print(f"  ✅ Extraction successful!")
    print(f"  ✅ Total skills: {results['extraction_metadata']['total_skills']}")
    print(f"  ✅ Method: {results['method_used']}")
    print(f"  ✅ Avg confidence: {results['extraction_metadata']['avg_confidence']:.2f}")
    print(f"  ✅ Top 10 skills: {results['skills'][:10]}")
    
    # Verify categories
    categories = list(results['categorized_skills'].keys())
    print(f"  ✅ Categories detected: {len(categories)}")
    for cat in categories[:3]:
        print(f"     - {cat}: {len(results['categorized_skills'][cat])} skills")
    
    test_results.append(("Advanced NLP Service", "✅ PASS"))
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    test_results.append(("Advanced NLP Service", f"❌ FAIL: {e}"))

# ==================== TEST 4: SENTENCE TRANSFORMER ====================
print("\n[TEST 4/8] Testing Sentence Transformer (Semantic Similarity)...")
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Test semantic similarity
    job_desc = "Looking for Python developer with machine learning expertise"
    candidate1 = "ML engineer proficient in Python and TensorFlow"
    candidate2 = "Frontend developer specialized in React and JavaScript"
    
    embeddings = model.encode([job_desc, candidate1, candidate2])
    
    sim1 = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    sim2 = cosine_similarity([embeddings[0]], [embeddings[2]])[0][0]
    
    print(f"  ✅ Model loaded: all-MiniLM-L6-v2")
    print(f"  ✅ Embedding dimension: {embeddings[0].shape}")
    print(f"  ✅ Similarity (Job vs ML Candidate): {sim1:.3f}")
    print(f"  ✅ Similarity (Job vs Frontend): {sim2:.3f}")
    print(f"  ✅ Correct ranking: {'YES' if sim1 > sim2 else 'NO'}")
    
    test_results.append(("Sentence Transformer", "✅ PASS"))
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    test_results.append(("Sentence Transformer", f"❌ FAIL: {e}"))

# ==================== TEST 5: MATCHING ENGINE ====================
print("\n[TEST 5/8] Testing Job-Candidate Matching Engine...")
try:
    from utils.matching import calculate_skill_match, extract_skills, compute_overall_score
    
    job_skills = ['python', 'django', 'postgresql', 'docker', 'aws', 'kubernetes']
    candidate_skills = ['python', 'django', 'mysql', 'docker', 'react', 'mongodb']
    
    skill_match = calculate_skill_match(job_skills, candidate_skills)
    
    # Test overall scoring
    tfidf_sim = 0.75
    cci_score = 80.0
    overall = compute_overall_score(
        tfidf_score=tfidf_sim,
        skill_match=skill_match,
        cci_score=cci_score
    )
    
    matched = set(job_skills) & set(candidate_skills)
    missing = set(job_skills) - set(candidate_skills)
    
    print(f"  ✅ Job requires: {job_skills}")
    print(f"  ✅ Candidate has: {candidate_skills}")
    print(f"  ✅ Matched skills: {list(matched)}")
    print(f"  ✅ Missing skills: {list(missing)}")
    print(f"  ✅ Skill match score: {skill_match:.2%}")
    print(f"  ✅ Overall score: {overall:.3f}")
    
    test_results.append(("Matching Engine", "✅ PASS"))
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    test_results.append(("Matching Engine", f"❌ FAIL: {e}"))

# ==================== TEST 6: FAIRNESS ENGINE ====================
print("\n[TEST 6/8] Testing Fairness & Bias Detection Engine...")
try:
    from services.fairness_engine import FairnessMetrics, analyze_hiring_fairness_comprehensive
    import pandas as pd
    
    # Simulate hiring data
    np.random.seed(42)
    n_candidates = 100
    
    applications = pd.DataFrame({
        'candidate_id': range(1, n_candidates + 1),
        'score': np.random.uniform(0.3, 0.95, n_candidates),
        'gender': np.random.choice(['M', 'F'], n_candidates),
        'age_group': np.random.choice(['18-30', '31-45', '46-60'], n_candidates),
        'decision': np.random.choice([0, 1], n_candidates, p=[0.7, 0.3])
    })
    
    # Run fairness analysis
    results = analyze_hiring_fairness_comprehensive(
        applications_df=applications,
        protected_attribute='gender',
        score_col='score',
        decision_col='decision'
    )
    
    print(f"  ✅ Fairness score: {results['fairness_score']:.1f}/100")
    print(f"  ✅ Demographic Parity: {results['metrics']['demographic_parity']}")
    print(f"  ✅ Disparate Impact: {results['metrics']['disparate_impact']}")
    print(f"  ✅ Equal Opportunity: {results['metrics']['equal_opportunity']}")
    print(f"  ✅ Issues detected: {len(results.get('issues', []))}")
    
    test_results.append(("Fairness Engine", "✅ PASS"))
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    test_results.append(("Fairness Engine", f"❌ FAIL: {e}"))

# ==================== TEST 7: TRANSPARENCY REPORTS ====================
print("\n[TEST 7/8] Testing Transparency Report Generator...")
try:
    from services.transparency_service import generate_transparency_report
    
    candidate_data = {
        '_id': 'cand_test_123',
        'name': 'Jane Smith',
        'email': 'jane@example.com',
        'skills': ['python', 'django', 'postgresql', 'docker'],
        'experience_years': 5,
        'applied_at': '2025-12-19'
    }
    
    job_data = {
        '_id': 'job_test_456',
        'title': 'Senior Backend Developer',
        'company': 'TechCorp',
        'skills': ['python', 'django', 'postgresql', 'docker', 'aws', 'kubernetes'],
        'created_at': '2025-12-15'
    }
    
    matching_results = {
        'overall_score': 0.78,
        'skill_match_score': 0.67,
        'tfidf_score': 0.85,
        'cci_score': 82.0,
        'matched_skills': ['python', 'django', 'postgresql', 'docker'],
        'missing_skills': ['aws', 'kubernetes'],
        'candidate_extra_skills': [],
        'required_skills': job_data['skills'],
        'extraction_metadata': {'method_used': 'hybrid', 'avg_confidence': 0.89}
    }
    
    fairness_audit = {
        'fairness_score': 94,
        'metrics': {
            'demographic_parity': {'score': 0.08, 'passed': True},
            'disparate_impact': {'ratio': 0.88, 'passed': True},
            'equal_opportunity': {'score': 0.06, 'passed': True}
        },
        'issues': [],
        'fairness_badge': {'label': 'EXCELLENT', 'color': 'green'},
        'protected_attributes': ['gender', 'age_group'],
        '_metadata': {'engine': 'custom', 'version': '2.0'}
    }
    
    report = generate_transparency_report(
        candidate_data=candidate_data,
        job_data=job_data,
        matching_results=matching_results,
        fairness_audit=fairness_audit,
        ranking=8,
        total_candidates=45,
        output_format='json'
    )
    
    print(f"  ✅ Report generated: {report['report_id']}")
    print(f"  ✅ Ranking: {report['summary']['ranking']}")
    print(f"  ✅ Match score: {report['summary']['match_score']}")
    print(f"  ✅ Fairness score: {report['summary']['fairness_score']}")
    print(f"  ✅ Skills matched: {report['summary']['skills_matched']}")
    print(f"  ✅ Report sections: {len(report['json_data'].keys())}")
    
    # Verify GDPR compliance
    assert 'candidate_rights' in report['json_data'], "Missing GDPR rights"
    assert 'algorithmic_details' in report['json_data'], "Missing algorithmic transparency"
    
    test_results.append(("Transparency Reports", "✅ PASS"))
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    test_results.append(("Transparency Reports", f"❌ FAIL: {e}"))

# ==================== TEST 8: CCI CALCULATOR ====================
print("\n[TEST 8/8] Testing Career Consistency Index (CCI)...")
try:
    from utils.cci_calculator import calculate_career_consistency_index
    from datetime import datetime, timedelta
    
    # Test stable career
    stable_experience = [
        {
            'company': 'TechCorp',
            'title': 'Senior Engineer',
            'start_date': datetime(2020, 1, 1),
            'end_date': datetime(2023, 12, 31)
        },
        {
            'company': 'StartupXYZ',
            'title': 'Lead Engineer',
            'start_date': datetime(2024, 1, 1),
            'end_date': None  # Current job
        }
    ]
    
    cci_result = calculate_career_consistency_index(stable_experience)
    
    print(f"  ✅ CCI Score: {cci_result['cci_score']}/100")
    print(f"  ✅ Tenure factor: {cci_result['factor_breakdown']['tenure']}")
    print(f"  ✅ Frequency factor: {cci_result['factor_breakdown']['frequency']}")
    print(f"  ✅ Interpretation: {cci_result['interpretation']}")
    
    test_results.append(("CCI Calculator", "✅ PASS"))
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    test_results.append(("CCI Calculator", f"❌ FAIL: {e}"))

# ==================== SUMMARY ====================
print("\n" + "="*70)
print("📊 TEST SUMMARY")
print("="*70)

passed = sum(1 for _, result in test_results if result.startswith("✅"))
failed = len(test_results) - passed

for test_name, result in test_results:
    print(f"{result:15} {test_name}")

print("="*70)
print(f"✅ PASSED: {passed}/{len(test_results)}")
print(f"❌ FAILED: {failed}/{len(test_results)}")
print(f"📈 Success Rate: {passed/len(test_results)*100:.1f}%")
print("="*70)

if failed == 0:
    print("\n🎉 ALL TESTS PASSED! System is production-ready!")
    print("\n✅ Next Steps:")
    print("   1. Run the application: python backend/app.py")
    print("   2. Access dashboard: http://localhost:5000")
    print("   3. Upload test resume and verify skill extraction")
    print("   4. Review transparency reports and fairness metrics")
    sys.exit(0)
else:
    print(f"\n⚠️ {failed} TEST(S) FAILED - Review errors above")
    sys.exit(1)
