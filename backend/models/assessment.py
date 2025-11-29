"""
Assessment and Quiz Models
Defines data structures for questions, quizzes, and quiz attempts
"""

from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId

class Question:
    """Individual quiz question"""
    
    def __init__(
        self,
        question_text: str,
        question_type: str = 'multiple_choice',  # multiple_choice, true_false, short_answer
        options: List[str] = None,
        correct_answer: str = '',
        correct_answers: List[str] = None,  # For multiple correct answers
        points: int = 1,
        difficulty: str = 'medium',  # easy, medium, hard
        category: str = 'general',
        tags: List[str] = None,
        explanation: str = '',
        created_by: str = '',
        time_limit: int = 60  # seconds per question
    ):
        self.question_text = question_text
        self.question_type = question_type
        self.options = options or []
        self.correct_answer = correct_answer
        self.correct_answers = correct_answers or []
        self.points = points
        self.difficulty = difficulty
        self.category = category
        self.tags = tags or []
        self.explanation = explanation
        self.created_by = created_by
        self.time_limit = time_limit
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True
        self.usage_count = 0
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        return {
            'question_text': self.question_text,
            'question_type': self.question_type,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'correct_answers': self.correct_answers,
            'points': self.points,
            'difficulty': self.difficulty,
            'category': self.category,
            'tags': self.tags,
            'explanation': self.explanation,
            'created_by': self.created_by,
            'time_limit': self.time_limit,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'usage_count': self.usage_count
        }

class Quiz:
    """Quiz/Assessment"""
    
    def __init__(
        self,
        title: str,
        description: str,
        created_by: str,
        questions: List[str] = None,  # List of question IDs
        duration: int = 3600,  # Total duration in seconds (default 60 minutes)
        passing_score: int = 70,  # Percentage
        total_points: int = 0,
        job_id: Optional[str] = None,
        is_required: bool = False,
        randomize_questions: bool = False,
        randomize_options: bool = False,
        show_results_immediately: bool = True,
        allow_review: bool = True,
        max_attempts: int = 1,
        tags: List[str] = None
    ):
        self.title = title
        self.description = description
        self.created_by = created_by
        self.questions = questions or []
        self.duration = duration
        self.passing_score = passing_score
        self.total_points = total_points
        self.job_id = job_id
        self.is_required = is_required
        self.randomize_questions = randomize_questions
        self.randomize_options = randomize_options
        self.show_results_immediately = show_results_immediately
        self.allow_review = allow_review
        self.max_attempts = max_attempts
        self.tags = tags or []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True
        self.attempts_count = 0
        self.average_score = 0.0
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        return {
            'title': self.title,
            'description': self.description,
            'created_by': self.created_by,
            'questions': self.questions,
            'duration': self.duration,
            'passing_score': self.passing_score,
            'total_points': self.total_points,
            'job_id': self.job_id,
            'is_required': self.is_required,
            'randomize_questions': self.randomize_questions,
            'randomize_options': self.randomize_options,
            'show_results_immediately': self.show_results_immediately,
            'allow_review': self.allow_review,
            'max_attempts': self.max_attempts,
            'tags': self.tags,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'attempts_count': self.attempts_count,
            'average_score': self.average_score
        }

class QuizAttempt:
    """Individual quiz attempt by a candidate"""
    
    def __init__(
        self,
        quiz_id: str,
        candidate_id: str,
        started_at: datetime = None,
        answers: Dict[str, any] = None,  # question_id -> answer
        time_spent: Dict[str, int] = None,  # question_id -> seconds
        score: float = 0.0,
        percentage: float = 0.0,
        passed: bool = False,
        status: str = 'in_progress'  # in_progress, completed, abandoned
    ):
        self.quiz_id = quiz_id
        self.candidate_id = candidate_id
        self.started_at = started_at or datetime.utcnow()
        self.answers = answers or {}
        self.time_spent = time_spent or {}
        self.score = score
        self.percentage = percentage
        self.passed = passed
        self.status = status
        self.completed_at = None
        self.total_time_spent = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.unanswered_count = 0
        self.feedback = {}  # question_id -> is_correct
    
    def to_dict(self):
        """Convert to dictionary for MongoDB"""
        return {
            'quiz_id': self.quiz_id,
            'candidate_id': self.candidate_id,
            'started_at': self.started_at,
            'answers': self.answers,
            'time_spent': self.time_spent,
            'score': self.score,
            'percentage': self.percentage,
            'passed': self.passed,
            'status': self.status,
            'completed_at': self.completed_at,
            'total_time_spent': self.total_time_spent,
            'correct_count': self.correct_count,
            'incorrect_count': self.incorrect_count,
            'unanswered_count': self.unanswered_count,
            'feedback': self.feedback
        }
