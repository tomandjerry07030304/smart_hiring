"""
Redis caching layer for performance optimization
"""

import os
import json
import logging
from typing import Optional, Any, Callable
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)

# Try to import Redis, but make it optional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - caching disabled")


class CacheManager:
    """Manages Redis caching with fallback to no-op if Redis unavailable"""
    
    def __init__(self):
        self.client = None
        self.enabled = False
        
        if REDIS_AVAILABLE:
            redis_url = os.getenv('REDIS_URL')
            if redis_url:
                try:
                    self.client = redis.from_url(
                        redis_url,
                        decode_responses=True,
                        socket_timeout=5,
                        socket_connect_timeout=5
                    )
                    # Test connection
                    self.client.ping()
                    self.enabled = True
                    logger.info("✅ Redis cache initialized successfully")
                except Exception as e:
                    logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                    self.client = None
                    self.enabled = False
        else:
            logger.info("Redis not configured - caching disabled")
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments"""
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float)):
                key_parts.append(str(arg))
        
        # Add keyword arguments (sorted for consistency)
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float)):
                key_parts.append(f"{k}:{v}")
        
        # Create hash for long keys
        key_str = ":".join(key_parts)
        if len(key_str) > 200:
            key_hash = hashlib.md5(key_str.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        
        return key_str
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default 5 minutes)
        """
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.enabled:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error: {e}")
            return 0
    
    def clear(self) -> bool:
        """Clear all cache (use with caution)"""
        if not self.enabled:
            return False
        
        try:
            self.client.flushdb()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False


# Global cache manager instance
cache_manager = CacheManager()


def cached(ttl: int = 300, key_prefix: str = "cache"):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds (default 5 minutes)
        key_prefix: Prefix for cache key
    
    Example:
        @cached(ttl=600, key_prefix="jobs")
        def get_active_jobs(company_id):
            # Expensive database query
            return jobs
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Skip caching if disabled
            if not cache_manager.enabled:
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache_manager._make_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Cache miss - execute function
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_prefix: str):
    """
    Invalidate all cache entries with given prefix
    
    Example:
        # After creating a job, invalidate jobs cache
        invalidate_cache("jobs")
    """
    if cache_manager.enabled:
        pattern = f"{key_prefix}:*"
        deleted = cache_manager.delete_pattern(pattern)
        logger.info(f"Invalidated {deleted} cache entries with prefix '{key_prefix}'")


# Export main components
__all__ = ['cache_manager', 'cached', 'invalidate_cache']
