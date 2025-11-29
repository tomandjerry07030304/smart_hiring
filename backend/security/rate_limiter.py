"""
Rate Limiting Implementation
Protects against brute force and DDoS attacks
"""

from flask import request, jsonify
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter using in-memory storage (Redis recommended for production)
    """
    
    def __init__(self):
        """Initialize rate limiter"""
        self._storage: Dict[str, list] = {}
        self._blocked: Dict[str, datetime] = {}
    
    def _get_client_key(self, identifier: Optional[str] = None) -> str:
        """
        Get unique key for client
        
        Args:
            identifier: Custom identifier (user_id, email, etc.)
        
        Returns:
            Client key
        """
        if identifier:
            return f"custom:{identifier}"
        
        # Use IP address as default
        return f"ip:{request.remote_addr}"
    
    def _cleanup_old_requests(self, key: str, window_seconds: int):
        """Remove requests outside the time window"""
        if key not in self._storage:
            return
        
        cutoff_time = datetime.utcnow() - timedelta(seconds=window_seconds)
        self._storage[key] = [
            timestamp for timestamp in self._storage[key]
            if timestamp > cutoff_time
        ]
    
    def is_rate_limited(
        self,
        identifier: Optional[str] = None,
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> bool:
        """
        Check if client is rate limited
        
        Args:
            identifier: Custom identifier
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            True if rate limited
        """
        key = self._get_client_key(identifier)
        
        # Check if blocked
        if key in self._blocked:
            if datetime.utcnow() < self._blocked[key]:
                return True
            else:
                del self._blocked[key]
        
        # Cleanup old requests
        self._cleanup_old_requests(key, window_seconds)
        
        # Initialize storage for new key
        if key not in self._storage:
            self._storage[key] = []
        
        # Check rate limit
        if len(self._storage[key]) >= max_requests:
            # Block for double the window time
            self._blocked[key] = datetime.utcnow() + timedelta(seconds=window_seconds * 2)
            logger.warning(f"🚫 Rate limit exceeded: {key}")
            return True
        
        # Add current request
        self._storage[key].append(datetime.utcnow())
        return False
    
    def get_remaining_requests(
        self,
        identifier: Optional[str] = None,
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> int:
        """Get number of remaining requests"""
        key = self._get_client_key(identifier)
        self._cleanup_old_requests(key, window_seconds)
        
        if key not in self._storage:
            return max_requests
        
        return max(0, max_requests - len(self._storage[key]))
    
    def reset_limit(self, identifier: Optional[str] = None):
        """Reset rate limit for a client"""
        key = self._get_client_key(identifier)
        
        if key in self._storage:
            del self._storage[key]
        
        if key in self._blocked:
            del self._blocked[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 60, window_seconds: int = 60, identifier_fn=None):
    """
    Decorator for rate limiting endpoints
    
    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        identifier_fn: Function to extract custom identifier from request
    
    Usage:
        @rate_limit(max_requests=5, window_seconds=60)
        def login():
            ...
        
        @rate_limit(max_requests=100, window_seconds=3600, identifier_fn=lambda: get_jwt_identity())
        def api_endpoint():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Get identifier
            identifier = None
            if identifier_fn:
                try:
                    identifier = identifier_fn()
                except:
                    pass
            
            # Check rate limit
            if rate_limiter.is_rate_limited(identifier, max_requests, window_seconds):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Please try again later.'
                }), 429
            
            # Add rate limit headers
            remaining = rate_limiter.get_remaining_requests(identifier, max_requests, window_seconds)
            response = fn(*args, **kwargs)
            
            if isinstance(response, tuple):
                response_obj, status_code = response[0], response[1]
            else:
                response_obj, status_code = response, 200
            
            # Add headers (if response object supports it)
            if hasattr(response_obj, 'headers'):
                response_obj.headers['X-RateLimit-Limit'] = str(max_requests)
                response_obj.headers['X-RateLimit-Remaining'] = str(remaining)
                response_obj.headers['X-RateLimit-Reset'] = str(window_seconds)
            
            return response_obj, status_code
        
        return wrapper
    return decorator


# Pre-configured rate limiters for common scenarios
def strict_rate_limit(fn):
    """
    Strict rate limit: 5 requests per minute
    Use for sensitive operations like login, password reset
    """
    return rate_limit(max_requests=5, window_seconds=60)(fn)


def standard_rate_limit(fn):
    """
    Standard rate limit: 60 requests per minute
    Use for general API endpoints
    """
    return rate_limit(max_requests=60, window_seconds=60)(fn)


def relaxed_rate_limit(fn):
    """
    Relaxed rate limit: 120 requests per minute
    Use for read-heavy endpoints
    """
    return rate_limit(max_requests=120, window_seconds=60)(fn)
