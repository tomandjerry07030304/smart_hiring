# AI INTERVIEWER MODULE
## Formal Technical Specification

**Document Version:** 1.0  
**Last Updated:** January 12, 2026  
**Classification:** Academic Project Documentation  

---

## 1. OFFICIAL DEFINITION

> **The AI Interviewer is a structured, AI-assisted interview orchestration system that selects, presents, and evaluates predefined domain-specific questions using rule-based logic and ML-based scoring — not a free-form conversational or generative agent.**

This definition must be used **consistently** across:
- PPT presentations
- Technical documentation
- Demo narrations
- Reviewer Q&A responses

---

## 2. SYSTEM CLASSIFICATION

| Attribute | Value |
|-----------|-------|
| **System Type** | Structured Intelligence / Rule-Based AI |
| **AI Category** | Non-Generative, Deterministic |
| **Input Modality** | Text only (current version) |
| **Decision Type** | Scoring, not hiring decisions |
| **Human Role** | Final decision authority |

---

## 3. CAPABILITIES MATRIX

### 3.1 What the AI Interviewer DOES

| Capability | Description | Technical Implementation |
|------------|-------------|-------------------------|
| **Question Selection** | Selects from predefined question banks based on job requirements | Maps `job.required_skills` to question categories in curated database |
| **Question Sequencing** | Orders questions from basic to advanced | `difficulty_levels = ['easy', 'medium', 'hard']` |
| **Skill-Based Targeting** | Matches job skills to relevant technical questions | Skill → Question Bank lookup with 10+ categories |
| **Answer Collection** | Accepts text responses via API | RESTful endpoint `/api/ai-interview/evaluate-answer` |
| **Keyword Scoring** | Evaluates responses against expected concepts | `_calculate_keyword_score()` matching against `expected_keywords` |
| **Feedback Generation** | Provides automated preliminary feedback | Score-based feedback templates |
| **Schedule Generation** | Creates interview timelines | Time allocation by segment (intro, technical, behavioral, wrap-up) |
| **Fairness Guarantee** | Ensures equal treatment | Same question pool for all candidates per job |

### 3.2 What the AI Interviewer Does NOT Do

| Excluded Capability | Reason for Exclusion |
|--------------------|--------------------|
| ❌ Generate new questions dynamically | Quality control; uses curated, validated questions only |
| ❌ Adapt difficulty based on resume analysis | Fairness: all candidates face equivalent difficulty |
| ❌ Analyze emotions or facial expressions | Not implemented; no video processing capability |
| ❌ Conduct voice conversations | Text-based only; no speech synthesis/recognition |
| ❌ Infer personality traits | Ethically problematic; scientifically unreliable |
| ❌ Make hiring decisions | Human recruiters retain final authority |
| ❌ Replace human interviewers | Assists and augments, does not replace |

---

## 4. TECHNICAL ARCHITECTURE

### 4.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    AI INTERVIEW MODULE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐    ┌──────────────────────────────┐  │
│  │  QUESTION BANK   │    │    QUESTION SELECTOR         │  │
│  │  ─────────────   │───▶│    ──────────────────        │  │
│  │  • Python (E/M/H)│    │    • Job Skills Input        │  │
│  │  • JavaScript    │    │    • Difficulty Distribution │  │
│  │  • SQL           │    │    • Category Balancing      │  │
│  │  • System Design │    │    • 60% Technical           │  │
│  │  • Behavioral    │    │    • 40% Behavioral          │  │
│  │  • Situational   │    └──────────────────────────────┘  │
│  └──────────────────┘                 │                     │
│                                       ▼                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              INTERVIEW SESSION                        │  │
│  │  ────────────────────────────────────────────────    │  │
│  │  • Present Questions Sequentially                    │  │
│  │  • Collect Text Responses                            │  │
│  │  • Track Time Limits                                 │  │
│  │  • Store Answers in Database                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                       │                     │
│                                       ▼                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ANSWER EVALUATOR                         │  │
│  │  ────────────────────────────────────────────────    │  │
│  │  • Keyword Matching (expected_keywords)              │  │
│  │  • Coverage Scoring (0-100%)                         │  │
│  │  • Detail Bonus (word count > 100)                   │  │
│  │  • Technical Term Detection                          │  │
│  │  • Feedback Generation                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                       │                     │
│                                       ▼                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              OUTPUT / REPORTING                       │  │
│  │  ────────────────────────────────────────────────    │  │
│  │  • Per-Question Scores                               │  │
│  │  • Overall Interview Score                           │  │
│  │  • Keyword Match Report                              │  │
│  │  • Preliminary Feedback                              │  │
│  │  • Data for Recruiter Dashboard                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Question Bank Structure

```python
question_structure = {
    'question_id': 'Q1',                    # Unique identifier
    'question_text': '...',                 # The actual question
    'skill': 'python',                      # Target skill
    'difficulty': 'medium',                 # easy | medium | hard
    'category': 'technical_fundamentals',   # Question category
    'expected_keywords': ['list', 'tuple'], # Scoring keywords
    'follow_up_question': '...',            # Optional follow-up
    'evaluation_criteria': [...],           # Rubric items
    'time_limit_minutes': 8                 # Suggested time
}
```

### 4.3 Scoring Algorithm

```python
def _calculate_keyword_score(answer, keywords):
    """
    Calculate score based on keyword presence
    
    Score = (matched_keywords / total_keywords) × 100
    Bonus: +10 if answer > 100 words (capped at 100)
    """
    matched = count_keywords_in_answer(answer, keywords)
    base_score = (matched / len(keywords)) * 100
    
    if word_count(answer) > 100:
        base_score = min(base_score + 10, 100)
    
    return base_score
```

---

## 5. API SPECIFICATION

### 5.1 Generate Questions

```http
POST /api/ai-interview/generate-questions
Authorization: Bearer <JWT>

Request:
{
    "job_id": "string",
    "num_questions": 10,
    "include_behavioral": true
}

Response:
{
    "message": "Interview questions generated successfully",
    "interview_set_id": "string",
    "questions": [...],
    "total_questions": 10
}
```

### 5.2 Evaluate Answer

```http
POST /api/ai-interview/evaluate-answer
Authorization: Bearer <JWT>

Request:
{
    "question_id": "Q1",
    "question": {...},
    "answer": "Candidate's text response"
}

Response:
{
    "question_id": "Q1",
    "auto_score": 75.5,
    "keyword_matches": ["list", "tuple"],
    "feedback": "Good answer with room for improvement.",
    "metrics": {
        "word_count": 85,
        "has_example": true,
        "is_detailed": true,
        "uses_technical_terms": true
    }
}
```

---

## 6. FAIRNESS GUARANTEES

### 6.1 Design Principles

1. **Standardization:** All candidates for the same job receive questions from the same pool
2. **Equal Difficulty:** Question difficulty distribution is fixed (not adaptive per candidate)
3. **Objective Scoring:** Keyword-based scoring removes subjective human bias
4. **Transparent Criteria:** Expected keywords and evaluation criteria are predefined
5. **Auditability:** All scores and decisions are logged with full explanation

### 6.2 Anti-Bias Measures

| Measure | Implementation |
|---------|----------------|
| No resume-based adaptation | Questions independent of resume content |
| Fixed difficulty curve | Same easy/medium/hard ratio for all |
| Blind scoring | Keyword matching doesn't know candidate identity |
| Standardized feedback | Template-based, not personalized criticism |

---

## 7. REVIEWER Q&A GUIDE

### Q: "Is this like ChatGPT conducting interviews?"

**Answer:** "No. This is structured AI, not generative AI. The system selects from a curated bank of 100+ predefined questions based on job requirements. It does not generate new questions or engage in free-form conversation. This ensures question quality, consistency, and fairness across all candidates."

### Q: "Can it understand what candidates are saying?"

**Answer:** "The system evaluates response relevance using keyword matching and NLP scoring. It identifies whether key technical concepts are mentioned and covered. It does not perform deep semantic comprehension or interpret nuanced meaning. This approach provides objective, consistent, and explainable scoring."

### Q: "How is this different from a human interviewer?"

**Answer:** "A human interviewer provides judgment, rapport, and contextual understanding. Our AI Interview System provides standardization, scalability, and preliminary screening. It assists recruiters by automating initial assessment, allowing human interviewers to focus on final-round candidates. It augments, not replaces, human judgment."

### Q: "Can it detect if someone is cheating?"

**Answer:** "The current text-based system does not include proctoring features. Interview integrity relies on the same trust model as written assessments. Proctoring and video monitoring are identified as future enhancements."

---

## 8. FUTURE SCOPE

| Feature | Priority | Description |
|---------|----------|-------------|
| Video Interview Recording | P2 | Record candidate video responses for recruiter review |
| Speech-to-Text Transcription | P2 | Convert audio responses to text for scoring |
| Adaptive Difficulty (Opt-in) | P3 | Optional mode where difficulty adjusts per performance |
| Semantic Answer Analysis | P3 | Use NLP models for deeper answer understanding |
| Proctoring Integration | P3 | Browser-based proctoring for integrity |

---

## 9. DOCUMENT HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-12 | System Audit | Initial formal specification |

---

*This document is the authoritative reference for all AI Interviewer descriptions and claims.*
