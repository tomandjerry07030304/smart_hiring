# REVIEWER QUICK REFERENCE CARD
## Smart Hiring System - Review-2 Preparation

**Print this card for easy reference during panel Q&A**

---

## SAFE ONE-LINERS

| Topic | Safe Statement |
|-------|----------------|
| **Project** | "Enterprise-grade, bias-aware Applicant Tracking System with AI-assisted screening" |
| **AI Interviewer** | "Structured interview system with predefined questions and automated scoring" |
| **Automation** | "End-to-end automated screening pipeline with human oversight for final decisions" |
| **Fairness** | "Quantitative bias detection using 9+ fairness metrics from academic literature" |
| **ML** | "Sentence-BERT semantic matching and TF-IDF with custom fairness engine" |

---

## TRAP QUESTION RESPONSES

### "Does the AI generate questions?"
> ❌ No. It **selects** from a curated bank of 100+ questions. This ensures quality and fairness.

### "Can it analyze video/emotions?"
> ❌ Current version is **text-based only**. Video/emotion analysis is future scope.

### "Is it like ChatGPT?"
> ❌ No. This is **structured AI** (rule-based + ML scoring), not **generative AI**.

### "Does it eliminate bias?"
> ⚠️ No system eliminates all bias. Ours **detects and quantifies** bias for human review.

### "Will it replace recruiters?"
> ❌ No. It **assists** recruiters with preliminary screening. Humans make final decisions.

---

## KEY NUMBERS TO REMEMBER

| Metric | Value |
|--------|-------|
| Question Bank Size | 100+ questions |
| Skill Database | 200+ skills |
| Fairness Metrics | 9+ |
| Scoring Algorithm | 60% skills + 40% experience |
| EEOC Threshold | 80% (Disparate Impact) |
| Protected Attributes | Gender, Age, Race (anonymized) |

---

## TECHNOLOGIES TO CITE

| Category | Technologies |
|----------|--------------|
| NLP | spaCy, Sentence-BERT (all-MiniLM-L6-v2) |
| ML | TF-IDF, Cosine Similarity, scikit-learn |
| Backend | Python 3.11, Flask 3.0, MongoDB |
| Security | JWT, 2FA (TOTP), RBAC, bcrypt |
| Fairness | NumPy/Pandas (no AIF360 dependency) |

---

## ACADEMIC REFERENCES

1. **Hardt et al. (2016)** - Equality of Opportunity in Supervised Learning *(Equal Opportunity, Equalized Odds)*
2. **EEOC (1978)** - Uniform Guidelines on Employee Selection *(80% Rule)*
3. **Speicher et al. (2018)** - Unified Approach to Quantifying Algorithmic Unfairness *(Theil Index)*
4. **IEEE 7000-2021** - Model Process for Addressing Ethical Concerns *(System Design)*

---

## WHAT TO DEMO ✅

1. Job posting with skill requirements
2. Resume upload → parsing → skill extraction
3. AI Interview question generation
4. Answer submission → keyword scoring
5. Candidate ranking dashboard
6. Fairness metrics display

## WHAT NOT TO DEMO ❌

1. Video/audio features (not implemented)
2. Real-time adaptive questions (not implemented)
3. "AI understanding" claims

---

## CONFIDENCE STATEMENTS

### Opening
> "Smart Hiring System is a production-ready ATS that combines automated screening with quantitative fairness auditing, designed for real-world deployment."

### Closing
> "Our system demonstrates that fair AI hiring is achievable through structured design, transparent algorithms, and continuous bias monitoring."

---

*Keep this card handy during your review presentation.*
