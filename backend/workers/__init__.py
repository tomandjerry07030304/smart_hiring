"""
Worker Queue System for Async Processing
Handles background jobs: resume parsing, analytics, email dispatch
"""

from .queue_manager import queue_manager
from .job_processor import JobProcessor

__all__ = ['queue_manager', 'JobProcessor']
