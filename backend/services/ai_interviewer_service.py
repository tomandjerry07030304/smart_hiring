"""
AI-Powered Interview System
Generates intelligent interview questions and provides automated interview assistance
"""

import re
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random


class AIInterviewerService:
    """
    AI-Powered Interview Question Generation and Analysis
    
    Features:
    - Auto-generate technical questions based on job requirements
    - Adaptive question difficulty based on candidate responses
    - Behavioral question generation aligned with company values
    - Interview scoring and evaluation
    - Question categorization (technical, behavioral, situational)
    """
    
    def __init__(self):
        self.question_templates = self._load_question_templates()
        self.difficulty_levels = ['easy', 'medium', 'hard']
        self.question_categories = [
            'technical_fundamentals',
            'problem_solving',
            'system_design',
            'behavioral',
            'situational',
            'culture_fit'
        ]
    
    def generate_interview_questions(
        self,
        job: Dict,
        candidate: Optional[Dict] = None,
        num_questions: int = 10,
        include_behavioral: bool = True
    ) -> List[Dict]:
        """
        Generate personalized interview questions for a candidate
        
        Args:
            job: Job details with required skills and description
            candidate: Optional candidate profile for personalization
            num_questions: Number of questions to generate
            include_behavioral: Whether to include behavioral questions
        
        Returns:
            List of interview questions with metadata
        """
        questions = []
        
        # Distribution of question types
        technical_count = int(num_questions * 0.6) if include_behavioral else num_questions
        behavioral_count = num_questions - technical_count
        
        # Generate technical questions based on required skills
        required_skills = job.get('required_skills', [])
        questions.extend(self._generate_technical_questions(required_skills, technical_count))
        
        # Generate behavioral questions
        if include_behavioral:
            questions.extend(self._generate_behavioral_questions(job, behavioral_count))
        
        # Add metadata
        for i, question in enumerate(questions, 1):
            question['question_id'] = f"Q{i}"
            question['order'] = i
            question['time_limit_minutes'] = self._get_time_limit(question['difficulty'])
        
        return questions
    
    def _generate_technical_questions(self, skills: List[str], count: int) -> List[Dict]:
        """Generate technical questions based on required skills"""
        questions = []
        
        if not skills:
            skills = ['general programming', 'problem solving']
        
        # Ensure we have enough questions
        while len(questions) < count:
            skill = random.choice(skills)
            difficulty = random.choice(self.difficulty_levels)
            
            question = self._get_technical_question(skill, difficulty)
            if question and question not in questions:
                questions.append(question)
        
        return questions[:count]
    
    def _get_technical_question(self, skill: str, difficulty: str) -> Optional[Dict]:
        """Get a technical question for specific skill and difficulty"""
        skill_lower = skill.lower()
        
        # Question bank by skill
        questions_bank = {
            'python': {
                'easy': [
                    {
                        'question': 'Explain the difference between lists and tuples in Python.',
                        'expected_keywords': ['mutable', 'immutable', 'performance', 'memory'],
                        'follow_up': 'When would you use a tuple over a list?'
                    },
                    {
                        'question': 'What is a Python decorator and give an example of its use?',
                        'expected_keywords': ['wrapper', 'function', 'syntax', '@'],
                        'follow_up': 'Can you write a simple logging decorator?'
                    }
                ],
                'medium': [
                    {
                        'question': 'Explain how Python\'s garbage collection works, specifically reference counting and cyclic references.',
                        'expected_keywords': ['reference counting', 'gc module', 'circular', 'memory'],
                        'follow_up': 'How can you force garbage collection?'
                    },
                    {
                        'question': 'What are context managers in Python? Implement a custom context manager.',
                        'expected_keywords': ['__enter__', '__exit__', 'with', 'resource management'],
                        'follow_up': 'How would you handle exceptions in a context manager?'
                    }
                ],
                'hard': [
                    {
                        'question': 'Explain the Python GIL (Global Interpreter Lock) and its implications for multi-threading.',
                        'expected_keywords': ['concurrency', 'multiprocessing', 'threading', 'performance'],
                        'follow_up': 'How would you achieve true parallelism in Python?'
                    }
                ]
            },
            'javascript': {
                'easy': [
                    {
                        'question': 'Explain the difference between var, let, and const in JavaScript.',
                        'expected_keywords': ['scope', 'hoisting', 'block', 'reassignment'],
                        'follow_up': 'What is the temporal dead zone?'
                    }
                ],
                'medium': [
                    {
                        'question': 'Explain closures in JavaScript with an example.',
                        'expected_keywords': ['scope', 'lexical', 'function', 'encapsulation'],
                        'follow_up': 'What are common use cases for closures?'
                    },
                    {
                        'question': 'What is the event loop in JavaScript? How does it handle asynchronous operations?',
                        'expected_keywords': ['call stack', 'callback queue', 'promises', 'async'],
                        'follow_up': 'Explain microtasks vs macrotasks.'
                    }
                ],
                'hard': [
                    {
                        'question': 'Explain prototypal inheritance in JavaScript and how it differs from classical inheritance.',
                        'expected_keywords': ['prototype', '__proto__', 'Object.create', 'constructor'],
                        'follow_up': 'How does ES6 class syntax relate to prototypes?'
                    }
                ]
            },
            'react': {
                'easy': [
                    {
                        'question': 'What are React Hooks? Explain useState and useEffect.',
                        'expected_keywords': ['state', 'side effects', 'functional components', 'lifecycle'],
                        'follow_up': 'What are the rules of Hooks?'
                    }
                ],
                'medium': [
                    {
                        'question': 'Explain React\'s Virtual DOM and reconciliation algorithm.',
                        'expected_keywords': ['diff', 'keys', 'performance', 'rendering'],
                        'follow_up': 'Why are keys important in lists?'
                    },
                    {
                        'question': 'What is the Context API and when should you use it instead of prop drilling?',
                        'expected_keywords': ['global state', 'provider', 'consumer', 'performance'],
                        'follow_up': 'How does Context compare to Redux?'
                    }
                ],
                'hard': [
                    {
                        'question': 'Explain React\'s Fiber architecture and how it enables concurrent rendering.',
                        'expected_keywords': ['reconciliation', 'scheduling', 'priority', 'interruption'],
                        'follow_up': 'What are the benefits of Suspense and Concurrent Mode?'
                    }
                ]
            },
            'sql': {
                'easy': [
                    {
                        'question': 'Explain the difference between INNER JOIN and LEFT JOIN.',
                        'expected_keywords': ['intersection', 'null', 'matching', 'tables'],
                        'follow_up': 'When would you use a RIGHT JOIN?'
                    }
                ],
                'medium': [
                    {
                        'question': 'What are database indexes? How do they improve query performance?',
                        'expected_keywords': ['B-tree', 'lookup', 'trade-off', 'write performance'],
                        'follow_up': 'What are the downsides of having too many indexes?'
                    }
                ],
                'hard': [
                    {
                        'question': 'Explain database normalization. What are the different normal forms and their purposes?',
                        'expected_keywords': ['1NF', '2NF', '3NF', 'redundancy', 'dependencies'],
                        'follow_up': 'When might you intentionally denormalize a database?'
                    }
                ]
            },
            'system design': {
                'medium': [
                    {
                        'question': 'Design a URL shortening service like bit.ly. What are the key components?',
                        'expected_keywords': ['hashing', 'database', 'collision', 'scalability'],
                        'follow_up': 'How would you handle high traffic?'
                    }
                ],
                'hard': [
                    {
                        'question': 'Design a distributed caching system. Discuss consistency, eviction policies, and scalability.',
                        'expected_keywords': ['LRU', 'consistent hashing', 'replication', 'CAP'],
                        'follow_up': 'How would you handle cache invalidation?'
                    }
                ]
            },
            'algorithms': {
                'easy': [
                    {
                        'question': 'Implement a function to reverse a string without using built-in reverse methods.',
                        'expected_keywords': ['iteration', 'two pointers', 'complexity'],
                        'follow_up': 'What is the time and space complexity?'
                    }
                ],
                'medium': [
                    {
                        'question': 'Explain the difference between BFS and DFS. When would you use each?',
                        'expected_keywords': ['queue', 'stack', 'shortest path', 'traversal'],
                        'follow_up': 'Implement BFS for a binary tree.'
                    }
                ],
                'hard': [
                    {
                        'question': 'Explain dynamic programming with an example. Solve the longest common subsequence problem.',
                        'expected_keywords': ['memoization', 'tabulation', 'optimal substructure', 'overlapping'],
                        'follow_up': 'What is the space optimization technique?'
                    }
                ]
            }
        }
        
        # Try to find questions for the specific skill
        for key in questions_bank:
            if key in skill_lower or skill_lower in key:
                if difficulty in questions_bank[key]:
                    question_data = random.choice(questions_bank[key][difficulty])
                    return {
                        'question_text': question_data['question'],
                        'skill': skill,
                        'difficulty': difficulty,
                        'category': 'technical_fundamentals',
                        'expected_keywords': question_data['expected_keywords'],
                        'follow_up_question': question_data.get('follow_up'),
                        'evaluation_criteria': self._get_evaluation_criteria(difficulty)
                    }
        
        # Generic technical question if skill not found
        return {
            'question_text': f'Explain your experience with {skill} and describe a complex problem you solved using it.',
            'skill': skill,
            'difficulty': difficulty,
            'category': 'technical_fundamentals',
            'expected_keywords': [skill, 'problem', 'solution', 'approach'],
            'follow_up_question': f'What challenges did you face and how did you overcome them?',
            'evaluation_criteria': self._get_evaluation_criteria(difficulty)
        }
    
    def _generate_behavioral_questions(self, job: Dict, count: int) -> List[Dict]:
        """Generate behavioral interview questions"""
        behavioral_templates = [
            {
                'question_text': 'Tell me about a time when you had to deal with a difficult team member. How did you handle it?',
                'category': 'behavioral',
                'competency': 'teamwork',
                'expected_keywords': ['communication', 'resolution', 'collaboration', 'outcome']
            },
            {
                'question_text': 'Describe a situation where you had to learn a new technology quickly. How did you approach it?',
                'category': 'behavioral',
                'competency': 'learning_agility',
                'expected_keywords': ['resources', 'practice', 'timeline', 'application']
            },
            {
                'question_text': 'Give an example of a project that didn\'t go as planned. What did you do?',
                'category': 'behavioral',
                'competency': 'problem_solving',
                'expected_keywords': ['pivot', 'analysis', 'adjustment', 'lesson']
            },
            {
                'question_text': 'Tell me about a time when you had to make a difficult technical decision with limited information.',
                'category': 'behavioral',
                'competency': 'decision_making',
                'expected_keywords': ['analysis', 'trade-offs', 'risk', 'outcome']
            },
            {
                'question_text': 'Describe a situation where you had to convince others to adopt your technical approach.',
                'category': 'behavioral',
                'competency': 'influence',
                'expected_keywords': ['persuasion', 'evidence', 'stakeholders', 'buy-in']
            },
            {
                'question_text': 'Tell me about your most challenging debugging experience.',
                'category': 'situational',
                'competency': 'technical_problem_solving',
                'expected_keywords': ['systematic', 'tools', 'root cause', 'resolution']
            },
            {
                'question_text': 'How do you prioritize tasks when you have multiple urgent deadlines?',
                'category': 'behavioral',
                'competency': 'time_management',
                'expected_keywords': ['impact', 'urgency', 'stakeholders', 'communication']
            },
            {
                'question_text': 'Describe a time when you received critical feedback. How did you respond?',
                'category': 'behavioral',
                'competency': 'growth_mindset',
                'expected_keywords': ['receptive', 'improvement', 'action', 'follow-up']
            }
        ]
        
        # Randomly select questions
        selected = random.sample(behavioral_templates, min(count, len(behavioral_templates)))
        
        for q in selected:
            q['difficulty'] = 'medium'
            q['time_limit_minutes'] = 10
            q['evaluation_criteria'] = [
                'Uses STAR method (Situation, Task, Action, Result)',
                'Provides specific examples',
                'Demonstrates self-awareness',
                'Shows positive outcome or learning'
            ]
        
        return selected
    
    def _get_evaluation_criteria(self, difficulty: str) -> List[str]:
        """Get evaluation criteria based on difficulty"""
        base_criteria = [
            'Understanding of core concepts',
            'Clarity of explanation',
            'Use of relevant examples'
        ]
        
        if difficulty == 'medium':
            base_criteria.extend([
                'Depth of technical knowledge',
                'Consideration of edge cases'
            ])
        elif difficulty == 'hard':
            base_criteria.extend([
                'Advanced understanding',
                'Trade-off analysis',
                'Real-world application experience',
                'Best practices awareness'
            ])
        
        return base_criteria
    
    def _get_time_limit(self, difficulty: str) -> int:
        """Get recommended time limit per question"""
        time_limits = {
            'easy': 5,
            'medium': 8,
            'hard': 12
        }
        return time_limits.get(difficulty, 8)
    
    def _load_question_templates(self) -> Dict:
        """Load question templates (can be expanded)"""
        return {}
    
    def evaluate_candidate_answer(
        self,
        question: Dict,
        answer: str,
        auto_score: bool = True
    ) -> Dict:
        """
        Evaluate a candidate's answer to an interview question
        
        Args:
            question: The interview question with metadata
            answer: Candidate's response
            auto_score: Whether to auto-score based on keywords
        
        Returns:
            Evaluation results with score and feedback
        """
        evaluation = {
            'question_id': question.get('question_id'),
            'answer_length': len(answer.split()),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if auto_score and 'expected_keywords' in question:
            score = self._calculate_keyword_score(answer, question['expected_keywords'])
            evaluation['auto_score'] = score
            evaluation['keyword_matches'] = self._find_keyword_matches(answer, question['expected_keywords'])
            evaluation['feedback'] = self._generate_answer_feedback(score, evaluation['keyword_matches'])
        else:
            evaluation['auto_score'] = None
            evaluation['feedback'] = 'Manual review required'
        
        # Answer quality metrics
        evaluation['metrics'] = {
            'word_count': len(answer.split()),
            'has_example': 'example' in answer.lower() or 'instance' in answer.lower(),
            'is_detailed': len(answer.split()) > 50,
            'uses_technical_terms': any(keyword.lower() in answer.lower() for keyword in question.get('expected_keywords', []))
        }
        
        return evaluation
    
    def _calculate_keyword_score(self, answer: str, keywords: List[str]) -> float:
        """Calculate score based on keyword presence"""
        answer_lower = answer.lower()
        matched = sum(1 for keyword in keywords if keyword.lower() in answer_lower)
        
        if not keywords:
            return 0.0
        
        score = (matched / len(keywords)) * 100
        
        # Bonus for detailed answers
        if len(answer.split()) > 100:
            score = min(score + 10, 100)
        
        return round(score, 2)
    
    def _find_keyword_matches(self, answer: str, keywords: List[str]) -> List[str]:
        """Find which keywords were mentioned"""
        answer_lower = answer.lower()
        return [kw for kw in keywords if kw.lower() in answer_lower]
    
    def _generate_answer_feedback(self, score: float, matched_keywords: List[str]) -> str:
        """Generate feedback based on auto-scoring"""
        if score >= 80:
            feedback = "Excellent answer! Covered all key concepts."
        elif score >= 60:
            feedback = "Good answer with room for improvement."
        elif score >= 40:
            feedback = "Partial answer. Consider elaborating on key points."
        else:
            feedback = "Answer lacks depth. Review the core concepts."
        
        if matched_keywords:
            feedback += f" Mentioned: {', '.join(matched_keywords[:5])}."
        
        return feedback
    
    def generate_interview_schedule(
        self,
        interview_type: str,
        duration_minutes: int = 60,
        start_time: Optional[datetime] = None
    ) -> Dict:
        """
        Generate an interview schedule with time allocations
        
        Args:
            interview_type: 'technical', 'behavioral', or 'mixed'
            duration_minutes: Total interview duration
            start_time: When interview starts
        
        Returns:
            Interview schedule with timing
        """
        if not start_time:
            start_time = datetime.utcnow()
        
        schedule = {
            'interview_type': interview_type,
            'duration_minutes': duration_minutes,
            'start_time': start_time.isoformat(),
            'segments': []
        }
        
        # Allocate time segments
        if interview_type == 'technical':
            segments = [
                {'name': 'Introduction', 'duration': 5, 'description': 'Welcome and overview'},
                {'name': 'Technical Questions', 'duration': duration_minutes - 15, 'description': 'Core technical assessment'},
                {'name': 'Candidate Questions', 'duration': 8, 'description': 'Q&A with candidate'},
                {'name': 'Wrap-up', 'duration': 2, 'description': 'Next steps'}
            ]
        elif interview_type == 'behavioral':
            segments = [
                {'name': 'Introduction', 'duration': 5, 'description': 'Welcome and overview'},
                {'name': 'Behavioral Questions', 'duration': duration_minutes - 15, 'description': 'STAR method questions'},
                {'name': 'Candidate Questions', 'duration': 8, 'description': 'Q&A with candidate'},
                {'name': 'Wrap-up', 'duration': 2, 'description': 'Next steps'}
            ]
        else:  # mixed
            segments = [
                {'name': 'Introduction', 'duration': 5, 'description': 'Welcome and overview'},
                {'name': 'Technical Questions', 'duration': int((duration_minutes - 15) * 0.6), 'description': 'Technical assessment'},
                {'name': 'Behavioral Questions', 'duration': int((duration_minutes - 15) * 0.4), 'description': 'Behavioral assessment'},
                {'name': 'Candidate Questions', 'duration': 8, 'description': 'Q&A with candidate'},
                {'name': 'Wrap-up', 'duration': 2, 'description': 'Next steps'}
            ]
        
        # Calculate start and end times for each segment
        current_time = start_time
        for segment in segments:
            segment['start_time'] = current_time.isoformat()
            current_time = current_time + timedelta(minutes=segment['duration'])
            segment['end_time'] = current_time.isoformat()
        
        schedule['segments'] = segments
        schedule['end_time'] = current_time.isoformat()
        
        return schedule


# Global instance
ai_interviewer = AIInterviewerService()


# Public API functions
def generate_interview_questions(job: Dict, candidate: Optional[Dict] = None, num_questions: int = 10) -> List[Dict]:
    """Generate interview questions for a job/candidate"""
    return ai_interviewer.generate_interview_questions(job, candidate, num_questions)


def evaluate_answer(question: Dict, answer: str) -> Dict:
    """Evaluate a candidate's answer"""
    return ai_interviewer.evaluate_candidate_answer(question, answer)


def create_interview_schedule(interview_type: str = 'mixed', duration: int = 60) -> Dict:
    """Create an interview schedule"""
    return ai_interviewer.generate_interview_schedule(interview_type, duration)
