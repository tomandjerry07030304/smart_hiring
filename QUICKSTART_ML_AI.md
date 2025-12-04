# Quick Start: ML & AI Features

## 🚀 Setup (5 minutes)

### 1. Install Dependencies
```bash
cd smart-hiring-system
pip install -r requirements.txt
```

### 2. Verify Installation
```python
python -c "from backend.services.ranking_service import rank_candidates_for_job; print('✅ ML Ready')"
python -c "from backend.services.ai_interviewer_service import generate_interview_questions; print('✅ AI Ready')"
```

### 3. Start Server
```bash
python run.py
```

---

## 📊 ML Candidate Ranking

### Basic Usage

**Rank all candidates for a job:**
```bash
POST /api/ai-interview/rank-candidates
{
  "job_id": "675a1b2c3d4e5f6789abcdef"
}
```

**Get detailed insights:**
```bash
GET /api/ai-interview/candidate-insights/{candidate_id}/{job_id}
```

### What You Get

- **ML Score**: 0-100 overall rating
- **Percentile**: Where candidate ranks vs others
- **Score Breakdown**: Skills (35%), Experience (25%), Resume Match (20%), Education (15%), Career Consistency (5%)
- **Strengths**: Top matched skills/qualifications
- **Weaknesses**: Missing skills/gaps
- **Interview Focus**: What to ask in interviews

### Example Response
```json
{
  "ml_score": 85.5,
  "percentile": 95,
  "strengths": ["Python", "Django", "AWS"],
  "weaknesses": ["React", "Docker"],
  "interview_focus": ["Technical depth in Python"]
}
```

---

## 🤖 AI Interview Assistant

### Generate Questions

```bash
POST /api/ai-interview/generate-questions
{
  "job_id": "675...",
  "num_questions": 10,
  "include_behavioral": true
}
```

**Returns**: 10 personalized questions with:
- Technical questions based on job skills
- Behavioral questions (STAR method)
- Difficulty levels (Easy/Medium/Hard)
- Time limits per question
- Expected answer keywords

### Evaluate Answers

```bash
POST /api/ai-interview/evaluate-answer
{
  "question": { /* question object */ },
  "answer": "Lists are mutable, tuples are immutable..."
}
```

**Returns**:
- Score (0-100)
- Keyword matches
- Feedback
- Strengths/improvements
- Follow-up questions

### Create Interview Schedule

```bash
POST /api/ai-interview/schedule
{
  "interview_type": "mixed",
  "duration_minutes": 60,
  "application_id": "675..."
}
```

---

## 🎯 Common Use Cases

### Use Case 1: Auto-Rank Applicants

```python
# When job receives applications, rank them
from backend.services.ranking_service import rank_candidates_for_job

candidates = db['candidates'].find({'applied_to': job_id})
job = db['jobs'].find_one({'_id': job_id})
ranked = rank_candidates_for_job(list(candidates), job)

# Top 3 candidates
top_3 = ranked[:3]
for candidate in top_3:
    print(f"{candidate['name']}: {candidate['ml_score']}")
```

### Use Case 2: Generate Interview Questions

```python
# Before interview, generate questions
from backend.services.ai_interviewer_service import generate_interview_questions

job = db['jobs'].find_one({'_id': job_id})
questions = generate_interview_questions(
    job=job,
    num_questions=8,
    include_behavioral=True
)

# Save for interviewer
db['interviews'].insert_one({
    'job_id': job_id,
    'questions': questions
})
```

### Use Case 3: Auto-Score Interview Answers

```python
# During/after interview, score answers
from backend.services.ai_interviewer_service import evaluate_answer

for q_and_a in interview_responses:
    evaluation = evaluate_answer(
        question=q_and_a['question'],
        answer=q_and_a['answer']
    )
    print(f"Score: {evaluation['score']}/10")
    print(f"Feedback: {evaluation['feedback']}")
```

---

## 🔧 Integration Points

### Frontend - Display ML Scores

```javascript
// In recruiter dashboard - application list
{applications.map(app => (
  <div key={app.id}>
    <h3>{app.candidate_name}</h3>
    <div className="ml-score">
      ML Score: {app.ml_score}/100
      <span className="percentile">Top {app.percentile}%</span>
    </div>
    <div className="strengths">
      ✓ {app.strengths.join(', ')}
    </div>
  </div>
))}
```

### Frontend - Interview Questions

```javascript
// Generate questions button
<button onClick={async () => {
  const response = await fetch('/api/ai-interview/generate-questions', {
    method: 'POST',
    body: JSON.stringify({ job_id: jobId, num_questions: 10 })
  });
  const data = await response.json();
  setQuestions(data.questions);
}}>
  Generate Interview Questions
</button>

// Display questions
{questions.map(q => (
  <div key={q.id} className="question">
    <h4>{q.question}</h4>
    <span className="difficulty">{q.difficulty}</span>
    <span className="time">{q.time_limit_minutes} min</span>
  </div>
))}
```

---

## 📈 Performance Tips

### 1. Cache ML Scores
```python
# Don't recalculate on every page load
if 'ml_score' not in application or not application['ml_score']:
    application['ml_score'] = calculate_ml_score(candidate, job)
    db['applications'].update_one({'_id': app_id}, {'$set': {'ml_score': application['ml_score']}})
```

### 2. Batch Ranking
```python
# Rank all candidates at once (more efficient)
all_candidates = db['candidates'].find({'applied_to': job_id})
ranked = rank_candidates_for_job(list(all_candidates), job)

# Update all applications with scores
for candidate in ranked:
    db['applications'].update_one(
        {'candidate_id': candidate['user_id'], 'job_id': job_id},
        {'$set': {'ml_score': candidate['ml_score']}}
    )
```

### 3. Pre-generate Questions
```python
# Generate questions when job is posted (not when interviewer needs them)
@job_routes.route('/create', methods=['POST'])
def create_job():
    job = create_new_job(data)
    
    # Pre-generate interview questions
    questions = generate_interview_questions(job, num_questions=10)
    db['interview_questions'].insert_one({
        'job_id': str(job['_id']),
        'questions': questions
    })
```

---

## ✅ Testing Checklist

- [ ] Install `scikit-learn` and `numpy`
- [ ] Import both services without errors
- [ ] Create test job with required_skills
- [ ] Create test candidate with resume_text and skills
- [ ] Call `/api/ai-interview/rank-candidates` - get ML scores
- [ ] Call `/api/ai-interview/generate-questions` - get questions
- [ ] Call `/api/ai-interview/evaluate-answer` - get score
- [ ] Verify ML scores appear in application list
- [ ] Verify interview questions display correctly

---

## 🐛 Quick Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'sklearn'`
```bash
pip install scikit-learn==1.3.2 numpy==1.24.3
```

**Problem**: ML scores are 0 or very low
- Check `resume_text` field is populated
- Check `skills` array is not empty
- Check job has `required_skills` defined
- View console logs for "ML RANKING" messages

**Problem**: No interview questions generated
- Check job has `required_skills` defined
- Check job skills match question bank (Python, JavaScript, React, SQL, etc.)
- View console logs for "AI INTERVIEW" messages

**Problem**: Can't access `/api/ai-interview/*` endpoints
- Check `backend/app.py` has `ai_interview_routes` imported
- Check blueprint is registered
- Restart server

---

## 📞 Need Help?

1. **Check logs**: Console shows detailed ML/AI operations with emoji indicators
2. **Test mode**: Use `scripts/create_sample_data.py` for test data
3. **Documentation**: See `ML_AI_FEATURES.md` for complete guide
4. **Support**: mightyazad@gmail.com

---

**Quick Links**:
- Full Documentation: `ML_AI_FEATURES.md`
- Ranking Service: `backend/services/ranking_service.py`
- AI Interviewer: `backend/services/ai_interviewer_service.py`
- API Routes: `backend/routes/ai_interview_routes.py`
