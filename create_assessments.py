"""
Generate sample assessment tests for candidates
Creates coding challenges, MCQ tests, and behavioral questions
"""

from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('mongodb://localhost:27017/')
db = client['smart_hiring_db']

# Sample assessments
assessments = [
    {
        'title': 'Python Coding Challenge',
        'type': 'coding',
        'job_id': None,  # Will be set to actual job
        'duration_minutes': 60,
        'questions': [
            {
                'question': 'Write a function to find the longest palindromic substring in a given string.',
                'test_cases': [
                    {'input': '"babad"', 'expected_output': '"bab" or "aba"'},
                    {'input': '"cbbd"', 'expected_output': '"bb"'}
                ],
                'points': 30
            },
            {
                'question': 'Implement a function to merge two sorted lists into one sorted list.',
                'test_cases': [
                    {'input': '[1,3,5], [2,4,6]', 'expected_output': '[1,2,3,4,5,6]'},
                    {'input': '[1,2,3], [4,5,6]', 'expected_output': '[1,2,3,4,5,6]'}
                ],
                'points': 25
            },
            {
                'question': 'Create a REST API endpoint to fetch user data from a database.',
                'description': 'Use Flask/FastAPI to create a GET /api/users/<id> endpoint',
                'points': 45
            }
        ],
        'pass_score': 60,
        'created_at': datetime.utcnow()
    },
    {
        'title': 'Technical MCQ - Python & Web Development',
        'type': 'mcq',
        'job_id': None,
        'duration_minutes': 30,
        'questions': [
            {
                'question': 'What is the output of: print([i**2 for i in range(5)])?',
                'options': [
                    '[0, 1, 4, 9, 16]',
                    '[1, 4, 9, 16, 25]',
                    '[0, 1, 2, 3, 4]',
                    'Error'
                ],
                'correct_answer': 0,
                'points': 5
            },
            {
                'question': 'Which HTTP method is idempotent?',
                'options': ['POST', 'GET', 'PATCH', 'All of the above'],
                'correct_answer': 1,
                'points': 5
            },
            {
                'question': 'What does CORS stand for?',
                'options': [
                    'Cross-Origin Resource Sharing',
                    'Cross-Origin Request Security',
                    'Common Origin Resource Sharing',
                    'Cross-Origin Remote Services'
                ],
                'correct_answer': 0,
                'points': 5
            },
            {
                'question': 'In MongoDB, which method is used to find a single document?',
                'options': ['find()', 'findOne()', 'find_one()', 'get()'],
                'correct_answer': 2,
                'points': 5
            },
            {
                'question': 'What is the purpose of JWT tokens?',
                'options': [
                    'Database encryption',
                    'Stateless authentication',
                    'File compression',
                    'Network routing'
                ],
                'correct_answer': 1,
                'points': 5
            }
        ],
        'pass_score': 70,
        'created_at': datetime.utcnow()
    },
    {
        'title': 'Behavioral & Cultural Fit',
        'type': 'behavioral',
        'job_id': None,
        'duration_minutes': 45,
        'questions': [
            {
                'question': 'Describe a challenging project you worked on. What was your role and how did you overcome obstacles?',
                'type': 'long_text',
                'points': 20
            },
            {
                'question': 'How do you handle conflicting priorities and tight deadlines?',
                'type': 'long_text',
                'points': 20
            },
            {
                'question': 'Give an example of when you had to learn a new technology quickly. How did you approach it?',
                'type': 'long_text',
                'points': 20
            },
            {
                'question': 'How do you ensure code quality and maintainability in your projects?',
                'type': 'long_text',
                'points': 20
            },
            {
                'question': 'Describe your experience working in agile/scrum teams.',
                'type': 'long_text',
                'points': 20
            }
        ],
        'pass_score': 60,
        'created_at': datetime.utcnow()
    },
    {
        'title': 'React Frontend Skills',
        'type': 'mcq',
        'job_id': None,
        'duration_minutes': 25,
        'questions': [
            {
                'question': 'What is the purpose of useEffect hook?',
                'options': [
                    'State management',
                    'Side effects and lifecycle',
                    'Event handling',
                    'Routing'
                ],
                'correct_answer': 1,
                'points': 10
            },
            {
                'question': 'How do you pass data from parent to child component?',
                'options': ['Context', 'Props', 'State', 'Redux'],
                'correct_answer': 1,
                'points': 10
            },
            {
                'question': 'What is JSX?',
                'options': [
                    'JavaScript XML syntax extension',
                    'Java Script Extension',
                    'JSON XML',
                    'JavaScript eXtreme'
                ],
                'correct_answer': 0,
                'points': 10
            }
        ],
        'pass_score': 70,
        'created_at': datetime.utcnow()
    }
]

print("\n" + "="*60)
print("📝 CREATING ASSESSMENT TESTS")
print("="*60)

# Get first job for demo
job = db.jobs.find_one({'title': 'Senior Python Developer'})

if job:
    print(f"\n📌 Creating assessments for: {job['title']}\n")
    
    for assessment in assessments:
        assessment['job_id'] = job['_id']
        result = db.assessments.insert_one(assessment)
        print(f"✅ {assessment['title']:40s} ({assessment['type']:10s}) - {len(assessment['questions'])} questions")

print("\n" + "="*60)
print(f"📊 Total assessments created: {db.assessments.count_documents({})}")
print("="*60)

# Show summary
print("\n📋 ASSESSMENT SUMMARY:")
print("-" * 60)
for assessment in db.assessments.find():
    total_points = sum(q.get('points', 0) for q in assessment['questions'])
    print(f"{assessment['title']:40s} | {total_points:3d} points | {assessment['duration_minutes']}min")

print("\n✅ Assessment system ready!")
print("   Candidates can now take tests as part of the hiring process\n")
