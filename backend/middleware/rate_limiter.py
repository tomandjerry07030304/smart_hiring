"""
Rate Limiting Middleware
Protects against brute force attacks and API abuse
"""

import time
from functools import wraps
from flask import request, jsonify
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """In-memory rate limiter (use Redis in production for distributed systems)"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.cleanup_interval = 60  # Clean old entries every 60 seconds
        self.last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Remove expired entries to prevent memory bloat"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            for key in list(self.requests.keys()):
                self.requests[key] = [
                    timestamp for timestamp in self.requests[key]
                    if current_time - timestamp < 3600  # Keep entries from last hour
                ]
                if not self.requests[key]:
                    del self.requests[key]
            self.last_cleanup = current_time
    
    def is_rate_limited(self, key: str, limit: int, window: int) -> Tuple[bool, dict]:
        """
        Check if request should be rate limited
        
        Args:
            key: Unique identifier (IP, user_id, etc.)
            limit: Maximum requests allowed
            window: Time window in seconds
        
        Returns:
            Tuple of (is_limited, rate_limit_info)
        """
        self._cleanup_old_entries()
        
        current_time = time.time()
        
        # Initialize or get existing request history
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove expired requests outside the window
        self.requests[key] = [
            timestamp for timestamp in self.requests[key]
            if current_time - timestamp < window
        ]
        
        # Check if limit exceeded
        request_count = len(self.requests[key])
        is_limited = request_count >= limit
        
        if not is_limited:
            self.requests[key].append(current_time)
        
        # Calculate reset time
        if self.requests[key]:
            oldest_request = min(self.requests[key])
            reset_time = int(oldest_request + window)
        else:
            reset_time = int(current_time + window)
        
        rate_info = {
            'limit': limit,
            'remaining': max(0, limit - request_count - (0 if is_limited else 1)),
            'reset': reset_time
        }
        
        return is_limited, rate_info


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(limit: int = 100, window: int = 60, key_func=None):
    """
    Rate limiting decorator
    
    Args:
        limit: Maximum requests allowed
        window: Time window in seconds
        key_func: Function to generate rate limit key (default: IP address)
    
    Example:
        @rate_limit(limit=5, window=60)  # 5 requests per minute
        def my_endpoint():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func()
            else:
                key = f"ip:{request.remote_addr}"
            
            # Check rate limit
            is_limited, rate_info = rate_limiter.is_rate_limited(key, limit, window)
            
            if is_limited:
                logger.warning(f"Rate limit exceeded for {key} on {request.path}")
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Please try again in {rate_info["reset"] - int(time.time())} seconds.',
                    'rate_limit': rate_info
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(rate_info['limit'])
                response.headers['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(rate_info['reset'])
                response.headers['Retry-After'] = str(rate_info['reset'] - int(time.time()))
                return response
            
            # Add rate limit headers to successful response
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(rate_info['limit'])
                response.headers['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(rate_info['reset'])
            
            return response
        
        return decorated_function
    return decorator


def get_user_rate_limit_key():
    """Get rate limit key based on authenticated user"""
    from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
    
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            if isinstance(identity, dict):
                user_id = identity.get('user_id', request.remote_addr)
            else:
                user_id = identity
            return f"user:{user_id}"
    except:
        pass
    
    return f"ip:{request.remote_addr}"
