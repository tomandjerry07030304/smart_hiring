# Smart Hiring System: Quick Start Guide

## ⚡ **5-Minute Launch Guide**

### **Step 1: Activate Environment**
```powershell
& "C:\Users\venkat anand\OneDrive\Desktop\4-2\.venv\Scripts\Activate.ps1"
cd smart-hiring-system
```

### **Step 2: Run System Test** (Optional but recommended)
```powershell
python test_system.py
```
Expected: **8/8 tests PASS** ✅

### **Step 3: Start Application**
```powershell
$env:FLASK_DEBUG='0'
python backend/app.py
```

### **Step 4: Access Dashboard**
- **URL:** http://localhost:5000
- **Login:** `recruiter@test.com` / `password123`

---

## 📋 **What's New in This Version**

### **Enhanced Features:**
1. **Advanced NLP Skill Extraction**
   - File: `backend/services/advanced_nlp_service.py`
   - Hybrid: Rule-based (2000+ skills) + ML (spaCy + BERT)
   - Confidence scoring + categorization

2. **Transparency Reports (GDPR)**
   - File: `backend/services/transparency_service.py`
   - PDF + JSON output
   - Explainable AI decisions

3. **Production ML Stack**
   - PyTorch 2.9.1
   - Transformers 4.57.3
   - Sentence-BERT (semantic similarity)
   - spaCy NER + en_core_web_sm

### **Already Excellent:**
- ✅ Fairness engine (5 metrics, IEEE 7000-2021)
- ✅ CCI calculator (job stability scoring)
- ✅ Matching engine (multi-factor weighted)

---

## 🧪 **Quick Test: Skill Extraction**

```powershell
python -c "
import sys; sys.path.insert(0, 'backend')
from services.advanced_nlp_service import get_skill_extractor

text = 'Python developer with React, Django, AWS, Docker, PostgreSQL experience'
extractor = get_skill_extractor()
result = extractor.extract_skills(text, method='hybrid')
print(f'Skills found: {result[\"skills\"][:10]}')
print(f'Total: {len(result[\"skills\"])} skills')
"
```

---

## 📊 **System Status**

| Component | Status | Details |
|-----------|--------|---------|
| ML Libraries | ✅ INSTALLED | PyTorch, Transformers, spaCy, NLTK |
| spaCy Model | ✅ DOWNLOADED | en_core_web_sm (12.8 MB) |
| NLTK Data | ✅ DOWNLOADED | punkt, stopwords, wordnet |
| Fairness Engine | ✅ READY | 5 metrics, bias detection |
| Transparency | ✅ READY | GDPR-compliant reports |
| Database | ✅ RUNNING | MongoDB localhost:27017 |
| Redis | ✅ RUNNING | Optional caching |

---

## 📚 **Key Documentation**

1. **`IMPLEMENTATION_COMPLETE.md`** - Full implementation summary
2. **`SYSTEM_ARCHITECTURE.md`** - Technical deep dive
3. **`INSTALLATION_COMPLETE.md`** - Setup verification guide
4. **`test_system.py`** - Automated test suite

---

## 🎯 **Common Tasks**

### **Upload Resume & Extract Skills:**
1. Login as candidate: `candidate@test.com`
2. Navigate to Resume Upload
3. Select PDF/DOCX file
4. View extracted skills (hybrid NLP)

### **View Fairness Metrics:**
1. Login as recruiter: `recruiter@test.com`
2. Navigate to Dashboard → Fairness Audit
3. View demographic parity, disparate impact, etc.

### **Generate Transparency Report:**
```python
from backend.services.transparency_service import generate_transparency_report

# Automatically generated for each candidate ranking
# Access via API: GET /api/audit/report/{candidate_id}
```

---

## ⚠️ **Troubleshooting**

### **Issue: Module not found**
```powershell
# Reinstall dependencies
pip install -r requirements_production.txt
```

### **Issue: spaCy model not found**
```powershell
python -m pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

### **Issue: Port 5000 already in use**
```powershell
# Use different port
$env:PORT='8000'
python backend/app.py
```

---

## 🚀 **Production Deployment**

### **Docker:**
```bash
docker build -t smart-hiring:latest .
docker run -p 5000:5000 --env-file .env smart-hiring:latest
```

### **Gunicorn (Production):**
```powershell
gunicorn backend.wsgi:app --bind 0.0.0.0:5000 --workers 4 --timeout 120
```

---

## 📧 **Support**

- **Technical:** mightyazad@gmail.com
- **Documentation:** See `SYSTEM_ARCHITECTURE.md`
- **Issues:** Run `test_system.py` for diagnostics

---

## ✅ **Verification Checklist**

Before deployment, verify:

- [ ] Test suite passes (8/8 tests)
- [ ] MongoDB running
- [ ] .env file configured
- [ ] Resume upload works
- [ ] Skill extraction accurate
- [ ] Fairness metrics displayed
- [ ] Transparency reports generated

---

**🎉 Your Smart Hiring System is Production-Ready!**

**Next:** Start the server and test with real resumes.
