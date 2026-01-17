# 🧪 Testing and Setup Guide

## Quick Start - Fix the Issues

### 1. ✅ Email Configuration (FIXED)

The email system was not sending emails because:
- `EMAIL_ENABLED` was not set (defaulted to false)
- SMTP credentials were placeholders

**To enable emails:**
```bash
# Edit .env file
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-actual-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
```

**For Gmail users:**
1. Go to https://myaccount.google.com/apppasswords
2. Create a new App Password for "Smart Hiring System"
3. Copy the 16-character password
4. Put it in `.env` as `SMTP_PASSWORD`

**Testing:**
- Register a new user → Should see email logs in console
- Apply to a job → Should see application confirmation email attempt
- Check console for detailed email debugging output

### 2. ✅ Assessments Tab (FIXED)

The assessments tab was empty because quizzes were filtered by job applications.

**What was fixed:**
- Changed `/api/assessments/quizzes` endpoint to show ALL active quizzes
- Candidates can now see and take assessments anytime
- Quizzes are marked as "required" if related to jobs they applied to

**Testing:**
1. Create a quiz as recruiter (see section below)
2. Switch to candidate account
3. Go to Assessments tab → Should now see all quizzes

### 3. 🔧 Resume Skills Extraction (ENHANCED)

Skills extraction was working but needed better visibility.

**What was added:**
- Detailed logging of resume processing
- Skills extraction debug output
- Console shows exactly which skills were found

**Testing:**
1. Upload a resume with technical skills (e.g., "Python, React, MongoDB")
2. Check browser console and terminal for logs
3. Skills should appear in:
   - Upload success message
   - Profile page skills section
   - Console output

**If skills aren't detected:**
- Make sure resume text is extractable (PDF format works best)
- Check console logs to see what text was extracted
- Skills must match entries in SKILLS_MASTER list (200+ skills)
- Common skills: python, java, javascript, react, node, mongodb, sql, etc.

### 4. 📊 Analytics Dashboard

**Prerequisites:**
- Must have applications submitted
- Must have job postings
- Database must have data

**Testing:**
1. Create jobs as recruiter
2. Apply to jobs as candidate
3. Go to Analytics tab → Should show charts and stats

---

## Creating Test Data

### Create Test Accounts

```python
# Run this in backend directory
python backend/create_test_accounts.py
```

This creates:
- Candidate: candidate@test.com / password123
- Recruiter: recruiter@test.com / password123  
- Admin: admin@test.com / password123

### Create Sample Quizzes

**Option 1: Via API (Postman/curl)**
```bash
# 1. Login as recruiter
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"recruiter@test.com","password":"password123"}'

# Save the token from response

# 2. Create questions
curl -X POST http://localhost:5000/api/assessments/questions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "What is Python used for?",
    "question_type": "multiple_choice",
    "options": ["Web Development", "Mobile Apps", "All of the above", "None"],
    "correct_answer": "All of the above",
    "points": 10,
    "difficulty": "easy",
    "category": "Python"
  }'

# 3. Create quiz (use question IDs from step 2)
curl -X POST http://localhost:5000/api/assessments/quizzes \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics Assessment",
    "description": "Test your Python knowledge",
    "questions": ["QUESTION_ID_1", "QUESTION_ID_2"],
    "duration": 1800,
    "passing_score": 70
  }'
```

**Option 2: Via UI**
1. Login as recruiter@test.com
2. Go to Questions tab → Create questions
3. Go to Quizzes tab → Create quiz
4. Add questions to quiz
5. Activate quiz

### Create Sample Jobs

1. Login as recruiter@test.com
2. Go to Jobs tab → Create New Job
3. Fill in:
   - Title: "Senior Python Developer"
   - Description: "Looking for Python expert"
   - Skills: python, django, postgresql, docker
   - Location: Remote
   - Job Type: Full-time
4. Save and publish

### Create Sample Resume

Create a test resume file (`test_resume.txt`):
```
John Doe
Full Stack Developer

SKILLS:
- Python, Django, Flask
- JavaScript, React, Node.js
- PostgreSQL, MongoDB, Redis
- Docker, Kubernetes, AWS
- Git, CI/CD

EXPERIENCE:
Senior Developer at Tech Corp (2020-2023)
- Built microservices with Python and Flask
- Developed React dashboards
- Managed PostgreSQL databases
```

Upload this via:
1. Login as candidate
2. Go to Profile tab
3. Click Upload Resume
4. Select test_resume.txt
5. Check console for extracted skills

---

## Verification Checklist

### ✅ Emails
- [ ] Registration email logged in console
- [ ] Application confirmation email attempt logged
- [ ] SMTP connection succeeds (if credentials configured)
- [ ] Email templates render correctly

### ✅ Assessments
- [ ] Quizzes visible in Assessments tab (candidate)
- [ ] Can start and complete quiz
- [ ] Quiz results saved
- [ ] Score displayed correctly

### ✅ Resume & Skills
- [ ] Resume uploads successfully
- [ ] Skills extracted and displayed
- [ ] Skills shown in profile
- [ ] Skills count correct in upload response

### ✅ Analytics
- [ ] Charts render without errors
- [ ] Stats calculated correctly
- [ ] Application history shows
- [ ] No console errors

---

## Common Issues & Solutions

### Issue: Assessments Still Empty
**Solution:** 
1. Verify database has quizzes: `db.quizzes.find({is_active: true})`
2. Check quiz creation was successful
3. Verify JWT token is valid
4. Check browser console for API errors

### Issue: Skills Not Showing
**Solution:**
1. Check console logs for "RESUME PROCESSING"
2. Verify resume text was extracted (should see text preview)
3. Check "Skills extracted" log shows count > 0
4. Try uploading a simple .txt file with skills listed
5. Verify skills match SKILLS_MASTER list

### Issue: Analytics Errors
**Solution:**
1. Verify pandas is installed: `pip install pandas==2.2.3`
2. Check database has applications
3. Look for errors in `/api/dashboard/analytics` endpoint
4. Check browser console for fetch errors

### Issue: Emails Not Sending
**Solution:**
1. Set `EMAIL_ENABLED=true` in .env
2. Use Gmail App Password (not regular password)
3. Check SMTP logs in console (detailed debugging enabled)
4. Verify firewall allows SMTP port 587

---

## Database Quick Checks

```javascript
// Connect to MongoDB
use smart_hiring_db

// Check users
db.users.count()
db.users.findOne()

// Check quizzes
db.quizzes.count()
db.quizzes.find({is_active: true})

// Check questions
db.questions.count()
db.questions.find({is_active: true})

// Check candidates
db.candidates.count()
db.candidates.findOne()

// Check applications
db.applications.count()
db.applications.find()
```

---

## Next Steps

1. **Enable Emails:** Configure SMTP in .env
2. **Create Test Data:** Run create_test_accounts.py
3. **Create Quizzes:** Use recruiter account to create sample quizzes
4. **Test Resume Upload:** Upload test resume with skills
5. **Verify Analytics:** Apply to jobs and check analytics dashboard
6. **Report Issues:** Note any remaining problems with specific error messages

---

## Getting Help

If issues persist, please provide:
1. **Console logs** from browser (F12 → Console)
2. **Terminal output** from Flask server
3. **Specific error messages**
4. **Steps to reproduce** the issue
5. **Expected vs actual** behavior

The system now has extensive logging to help debug any issues!