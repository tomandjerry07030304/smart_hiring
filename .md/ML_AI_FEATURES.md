# ML & AI Features Documentation

## Overview

Smart Hiring System now includes two powerful AI-driven features:

1. **ML Candidate Ranking** - Intelligent candidate scoring and ranking using machine learning
2. **AI Interview Assistant** - Automated interview question generation and answer evaluation

---

## 🎯 ML Candidate Ranking

### Features

- **Resume-Job Matching**: TF-IDF vectorization with cosine similarity
- **Skills Scoring**: Jaccard similarity between candidate and job skills
- **Experience Matching**: Smart experience level comparison (detects overqualification)
- **Education Scoring**: Qualification level comparison
- **Career Consistency**: Integration with Career Consistency Index (CCI)
- **Explainability**: Detailed breakdown of strengths and weaknesses
- **Interview Focus**: Recommendations on what to assess in interviews

### Scoring Algorithm

The ML model uses a weighted scoring system:

```
Total Score = (Skills × 35%) + (Experience × 25%) + (Resume Similarity × 20%) + 
              (Education × 15%) + (Career Consistency × 5%)
```

### API Endpoints

#### 1. Rank Candidates for Job

**POST** `/api/ai-interview/rank-candidates`

```json
{
  "job_id": "675..."
}
```

**Response**:
```json
{
  "job_id": "675...",
  "job_title": "Senior Python Developer",
  "total_candidates": 5,
  "ranked_candidates": [
    {
      "_id": "675...",
      "name": "John Doe",
      "email": "john@example.com",
      "ml_score": 85.5,
      "percentile": 95,
      "skill_match_score": 90,
      "experience_score": 85,
      "resume_similarity_score": 80,
      "education_score": 85,
      "cci_score": 88,
      "strengths": ["Python", "Django", "AWS"],
      "weaknesses": ["React", "Docker"],
      "interview_focus": ["Technical depth in Python", "Cloud architecture experience"]
    }
  ]
}
```

#### 2. Get Candidate Insights

**GET** `/api/ai-interview/candidate-insights/{candidate_id}/{job_id}`

**Response**:
```json
{
  "candidate_name": "John Doe",
  "job_title": "Senior Python Developer",
  "overall_score": 85.5,
  "score_breakdown": {
    "skills": 90,
    "experience": 85,
    "resume_similarity": 80,
    "education": 85,
    "career_consistency": 88
  },
  "strengths": ["Python", "Django", "AWS"],
  "weaknesses": ["React", "Docker"],
  "recommendation": "Strong candidate with excellent Python skills",
  "interview_focus": ["Technical depth in Python", "Cloud architecture experience"]
}
```

### Usage Example

```python
from backend.services.ranking_service import rank_candidates_for_job, get_candidate_insights

# Rank all candidates for a job
candidates = db['candidates'].find()
job = db['jobs'].find_one({'_id': job_id})
ranked = rank_candidates_for_job(list(candidates), job)

# Get detailed insights for one candidate
insights = get_candidate_insights(candidate, job)
```

### Fallback Mode

If `scikit-learn` is not installed, the service automatically falls back to basic scoring:
- Skills: Jaccard similarity
- Experience: Simple range matching
- No TF-IDF vectorization

---

## 🤖 AI Interview Assistant

### Features

- **Question Generation**: Auto-generate questions based on job requirements and candidate skills
- **50+ Question Bank**: Curated questions for Python, JavaScript, React, SQL, algorithms, system design
- **3 Difficulty Levels**: Easy (5 min), Medium (8 min), Hard (12 min)
- **Question Types**: Technical, Behavioral (STAR method), Situational, Culture Fit
- **Auto-Scoring**: Keyword-based evaluation of candidate answers
- **Answer Evaluation**: Detailed feedback with strengths and areas for improvement
- **Interview Scheduling**: Time allocation and question ordering

### Question Categories

1. **Technical Fundamentals**: Language-specific questions (Python, JS, React, SQL)
2. **Problem Solving**: Algorithms, data structures, optimization
3. **System Design**: Architecture, scalability, design patterns
4. **Behavioral**: STAR method questions about past experiences
5. **Situational**: "What would you do if..." scenarios
6. **Culture Fit**: Values, work style, team collaboration

### API Endpoints

#### 1. Generate Interview Questions

**POST** `/api/ai-interview/generate-questions`

```json
{
  "job_id": "675...",
  "num_questions": 10,
  "include_behavioral": true
}
```

**Response**:
```json
{
  "message": "Interview questions generated successfully",
  "interview_set_id": "675...",
  "total_questions": 10,
  "questions": [
    {
      "id": "Q1",
      "category": "technical_fundamentals",
      "skill": "Python",
      "difficulty": "medium",
      "question": "Explain the difference between a list and a tuple in Python. When would you use each?",
      "expected_keywords": ["immutable", "mutable", "performance", "memory"],
      "time_limit_minutes": 8,
      "points": 10
    }
  ]
}
```

#### 2. Get Interview Questions

**GET** `/api/ai-interview/questions/{job_id}`

Returns the latest question set for a job.

#### 3. Evaluate Answer

**POST** `/api/ai-interview/evaluate-answer`

```json
{
  "question": {
    "id": "Q1",
    "question": "Explain the difference between a list and a tuple...",
    "expected_keywords": ["immutable", "mutable", "performance"],
    "difficulty": "medium"
  },
  "answer": "Lists are mutable and can be changed after creation. Tuples are immutable and cannot be modified. Tuples use less memory and are faster for iteration."
}
```

**Response**:
```json
{
  "score": 8.5,
  "max_score": 10,
  "percentage": 85,
  "keyword_match_count": 3,
  "total_keywords": 4,
  "feedback": "Strong answer covering key concepts",
  "strengths": ["Correctly explained mutability", "Mentioned performance"],
  "areas_for_improvement": ["Could elaborate on use cases"],
  "follow_up_questions": ["Can you provide an example of when you'd use a tuple?"]
}
```

#### 4. Create Interview Schedule

**POST** `/api/ai-interview/schedule`

```json
{
  "interview_type": "mixed",  // technical, behavioral, or mixed
  "duration_minutes": 60,
  "application_id": "675..."
}
```

**Response**:
```json
{
  "total_duration_minutes": 60,
  "sections": [
    {
      "section": "Technical",
      "duration_minutes": 40,
      "num_questions": 5
    },
    {
      "section": "Behavioral",
      "duration_minutes": 20,
      "num_questions": 3
    }
  ],
  "recommended_questions": [...]
}
```

### Usage Example

```python
from backend.services.ai_interviewer_service import (
    generate_interview_questions,
    evaluate_answer,
    create_interview_schedule
)

# Generate questions for a job
questions = generate_interview_questions(
    job=job_doc,
    num_questions=10,
    include_behavioral=True
)

# Evaluate a candidate's answer
evaluation = evaluate_answer(question, candidate_answer)

# Create interview schedule
schedule = create_interview_schedule('mixed', 60)
```

---

## 🚀 Setup & Installation

### 1. Install Dependencies

```bash
pip install scikit-learn==1.3.2 numpy==1.24.3
```

Or use the updated `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```python
# Test ML ranking
from backend.services.ranking_service import rank_candidates_for_job
print("✅ ML Ranking service loaded")

# Test AI interviewer
from backend.services.ai_interviewer_service import generate_interview_questions
print("✅ AI Interviewer service loaded")
```

### 3. API Routes

The routes are automatically registered in `app.py` under `/api/ai-interview/`.

---

## 📊 Integration with Existing Features

### With Application System

```python
# When a candidate applies, calculate ML score
from backend.services.ranking_service import get_candidate_insights

application = {
    'candidate_id': candidate_id,
    'job_id': job_id,
    'ml_score': None,
    'ml_insights': None
}

# Get ML insights
insights = get_candidate_insights(candidate, job)
application['ml_score'] = insights['overall_score']
application['ml_insights'] = insights

db['applications'].insert_one(application)
```

### With Interview Scheduling

```python
# When scheduling an interview, generate questions
from backend.services.ai_interviewer_service import generate_interview_questions

questions = generate_interview_questions(
    job=job,
    num_questions=8,
    include_behavioral=True
)

# Save to database
db['interview_questions'].insert_one({
    'application_id': app_id,
    'questions': questions,
    'created_at': datetime.utcnow()
})
```

---

## 🧪 Testing

### Test ML Ranking

```python
# Create test candidates and job
candidates = [
    {
        'user_id': 'test1',
        'resume_text': 'Python developer with 5 years experience in Django and AWS',
        'skills': ['Python', 'Django', 'AWS'],
        'experience_years': 5,
        'education_level': 'bachelors'
    }
]

job = {
    'title': 'Senior Python Developer',
    'description': 'Looking for Python developer with Django and AWS experience',
    'required_skills': ['Python', 'Django'],
    'preferred_skills': ['AWS', 'Docker'],
    'min_experience_years': 3,
    'education_requirement': 'bachelors'
}

# Rank
from backend.services.ranking_service import rank_candidates_for_job
ranked = rank_candidates_for_job(candidates, job)
print(f"Top candidate score: {ranked[0]['ml_score']}")
```

### Test AI Interviewer

```python
# Generate questions
from backend.services.ai_interviewer_service import generate_interview_questions

questions = generate_interview_questions(
    job={'required_skills': ['Python', 'JavaScript']},
    num_questions=5
)
print(f"Generated {len(questions)} questions")

# Evaluate answer
from backend.services.ai_interviewer_service import evaluate_answer

question = questions[0]
answer = "Lists are mutable, tuples are immutable"
evaluation = evaluate_answer(question, answer)
print(f"Score: {evaluation['score']}/{evaluation['max_score']}")
```

---

## 🎨 Frontend Integration

### Display ML Score in Application List

```javascript
// Fetch applications with ML scores
fetch('/api/ai-interview/rank-candidates', {
  method: 'POST',
  body: JSON.stringify({ job_id: jobId })
})
.then(res => res.json())
.then(data => {
  data.ranked_candidates.forEach(candidate => {
    console.log(`${candidate.name}: ${candidate.ml_score}/100`);
  });
});
```

### Show Interview Questions

```javascript
// Generate questions
fetch('/api/ai-interview/generate-questions', {
  method: 'POST',
  body: JSON.stringify({
    job_id: jobId,
    num_questions: 10
  })
})
.then(res => res.json())
.then(data => {
  displayQuestions(data.questions);
});
```

### Evaluate Answers

```javascript
// Submit answer for evaluation
fetch('/api/ai-interview/evaluate-answer', {
  method: 'POST',
  body: JSON.stringify({
    question: currentQuestion,
    answer: userAnswer
  })
})
.then(res => res.json())
.then(evaluation => {
  showScore(evaluation.score, evaluation.feedback);
});
```

---

## ⚙️ Configuration

### ML Ranking Weights

Edit `backend/services/ranking_service.py`:

```python
WEIGHTS = {
    'skills': 0.35,        # 35% - Skills matching
    'experience': 0.25,    # 25% - Experience level
    'similarity': 0.20,    # 20% - Resume similarity
    'education': 0.15,     # 15% - Education level
    'cci': 0.05           # 5% - Career consistency
}
```

### AI Interview Settings

Edit `backend/services/ai_interviewer_service.py`:

```python
TIME_LIMITS = {
    'easy': 5,      # 5 minutes
    'medium': 8,    # 8 minutes
    'hard': 12      # 12 minutes
}

POINTS = {
    'easy': 5,
    'medium': 10,
    'hard': 15
}
```

---

## 📈 Performance Optimization

### Caching ML Scores

```python
# Cache ML scores for 24 hours
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_ml_score(candidate_id, job_id):
    return calculate_ml_score(candidate_id, job_id)
```

### Batch Processing

```python
# Rank candidates in batches
from backend.services.ranking_service import rank_candidates_for_job

def rank_all_applications(job_id):
    applications = db['applications'].find({'job_id': job_id})
    candidates = [get_candidate(app['candidate_id']) for app in applications]
    
    # Rank all at once (more efficient than one-by-one)
    ranked = rank_candidates_for_job(candidates, job)
    return ranked
```

---

## 🔒 Security Considerations

1. **Authorization**: Only recruiters/companies can access ML rankings
2. **Data Privacy**: ML scores are not visible to candidates
3. **Rate Limiting**: Consider rate limits on AI question generation
4. **Input Validation**: All user inputs are validated before processing

---

## 📝 Changelog

### Version 1.0 (Current)

- ✅ ML Candidate Ranking with TF-IDF and weighted scoring
- ✅ AI Interview Question Generation (50+ questions)
- ✅ Auto-scoring of candidate answers
- ✅ Interview schedule generation
- ✅ Explainability features (strengths/weaknesses)
- ✅ Integration with existing application system
- ✅ Fallback mode when scikit-learn unavailable

### Planned Features

- 🔄 Video interview analysis (facial recognition, speech-to-text)
- 🔄 Custom question bank management
- 🔄 ML model retraining based on hiring outcomes
- 🔄 Bias detection in scoring
- 🔄 Multi-language support for questions

---

## 🆘 Troubleshooting

### ML Ranking not working

1. Check if `scikit-learn` is installed:
   ```bash
   pip list | grep scikit-learn
   ```

2. Test import:
   ```python
   from backend.services.ranking_service import rank_candidates_for_job
   ```

3. Check logs for errors:
   ```bash
   # Look for "ML RANKING ERROR" in console
   ```

### AI Questions not generating

1. Verify job has `required_skills`:
   ```python
   job = db['jobs'].find_one({'_id': job_id})
   print(job.get('required_skills'))
   ```

2. Check if question bank loaded:
   ```python
   from backend.services.ai_interviewer_service import QUESTION_BANK
   print(len(QUESTION_BANK))  # Should be 50+
   ```

### Low ML Scores

Candidates getting low scores? Check:
- Resume text extraction working (`resume_text` field populated)
- Skills are being extracted correctly
- Job requirements are well-defined
- Experience levels match expectations

---

## 📞 Support

For questions or issues:
- Email: mightyazad@gmail.com
- Check logs: Console output shows detailed ML/AI operations
- Test mode: Use sample data from `scripts/create_sample_data.py`

---

**Last Updated**: December 2024  
**Version**: 1.0.0
