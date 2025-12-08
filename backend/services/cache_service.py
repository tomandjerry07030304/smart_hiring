"""
Redis Caching Service
=====================
Enterprise-grade caching layer with Redis

Features:
- Simple key-value caching
- TTL (time-to-live) support
- Cache tags for bulk invalidation
- Cache warming
- Statistics and monitoring
- Fallback to memory cache if Redis unavailable

Common Use Cases:
- User session data
- API response caching
- Database query results
- Job listing cache
- Candidate search results
- Assessment results

Author: Smart Hiring System Team
Date: December 2025
"""

import logging
import json
import pickle
from typing import Any, Optional, List, Dict, Union
from datetime import timedelta
import redis
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)


class CacheService:
    """
    Redis-based caching service with automatic fallback
    """
    
    def __init__(self, redis_url: str = None, default_ttl: int = 3600):
        """
        Initialize cache service
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds (1 hour default)
        """
        self.default_ttl = default_ttl
        self.redis_client = None
        self.memory_cache = {}  # Fallback in-memory cache
        self.use_redis = False
        
        if redis_url:
            try:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=False,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True
                )
                # Test connection
                self.redis_client.ping()
                self.use_redis = True
                logger.info(f"✅ Redis cache connected: {redis_url}")
            except Exception as e:
                logger.warning(f"⚠️ Redis unavailable, using memory cache: {e}")
        else:
            logger.info("⚠️ No Redis URL provided, using memory cache")
    
    def _make_key(self, key: str, prefix: str = "cache") -> str:
        """Create namespaced cache key"""
        return f"{prefix}:{key}"
    
    def get(self, key: str, prefix: str = "cache") -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            prefix: Key namespace prefix
        
        Returns:
            Cached value or None if not found
        """
        full_key = self._make_key(key, prefix)
        
        try:
            if self.use_redis:
                value = self.redis_client.get(full_key)
                if value is not None:
                    return pickle.loads(value)
            else:
                return self.memory_cache.get(full_key)
        except Exception as e:
            logger.error(f"Cache get error for {full_key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, prefix: str = "cache") -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default_ttl if None)
            prefix: Key namespace prefix
        
        Returns:
            True if successful
        """
        full_key = self._make_key(key, prefix)
        ttl = ttl or self.default_ttl
        
        try:
            if self.use_redis:
                serialized = pickle.dumps(value)
                self.redis_client.setex(full_key, ttl, serialized)
            else:
                self.memory_cache[full_key] = value
            
            return True
        except Exception as e:
            logger.error(f"Cache set error for {full_key}: {e}")
            return False
    
    def delete(self, key: str, prefix: str = "cache") -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key
            prefix: Key namespace prefix
        
        Returns:
            True if successful
        """
        full_key = self._make_key(key, prefix)
        
        try:
            if self.use_redis:
                self.redis_client.delete(full_key)
            else:
                self.memory_cache.pop(full_key, None)
            
            return True
        except Exception as e:
            logger.error(f"Cache delete error for {full_key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str, prefix: str = "cache") -> int:
        """
        Delete all keys matching pattern
        
        Args:
            pattern: Key pattern (e.g., "user_*")
            prefix: Key namespace prefix
        
        Returns:
            Number of keys deleted
        """
        full_pattern = self._make_key(pattern, prefix)
        deleted_count = 0
        
        try:
            if self.use_redis:
                keys = self.redis_client.keys(full_pattern)
                if keys:
                    deleted_count = self.redis_client.delete(*keys)
            else:
                keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(full_pattern)]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                deleted_count = len(keys_to_delete)
            
            logger.info(f"Deleted {deleted_count} keys matching {full_pattern}")
            return deleted_count
        except Exception as e:
            logger.error(f"Cache delete pattern error for {full_pattern}: {e}")
            return 0
    
    def exists(self, key: str, prefix: str = "cache") -> bool:
        """Check if key exists in cache"""
        full_key = self._make_key(key, prefix)
        
        try:
            if self.use_redis:
                return bool(self.redis_client.exists(full_key))
            else:
                return full_key in self.memory_cache
        except Exception as e:
            logger.error(f"Cache exists error for {full_key}: {e}")
            return False
    
    def get_ttl(self, key: str, prefix: str = "cache") -> Optional[int]:
        """Get remaining TTL for key in seconds"""
        full_key = self._make_key(key, prefix)
        
        try:
            if self.use_redis:
                return self.redis_client.ttl(full_key)
        except Exception as e:
            logger.error(f"Cache TTL error for {full_key}: {e}")
        
        return None
    
    def get_many(self, keys: List[str], prefix: str = "cache") -> Dict[str, Any]:
        """
        Get multiple values at once
        
        Args:
            keys: List of cache keys
            prefix: Key namespace prefix
        
        Returns:
            Dictionary of key-value pairs
        """
        results = {}
        
        for key in keys:
            value = self.get(key, prefix)
            if value is not None:
                results[key] = value
        
        return results
    
    def set_many(self, data: Dict[str, Any], ttl: Optional[int] = None, prefix: str = "cache") -> bool:
        """
        Set multiple values at once
        
        Args:
            data: Dictionary of key-value pairs
            ttl: Time to live in seconds
            prefix: Key namespace prefix
        
        Returns:
            True if all successful
        """
        success = True
        
        for key, value in data.items():
            if not self.set(key, value, ttl, prefix):
                success = False
        
        return success
    
    def increment(self, key: str, amount: int = 1, prefix: str = "cache") -> Optional[int]:
        """
        Increment numeric value
        
        Args:
            key: Cache key
            amount: Amount to increment by
            prefix: Key namespace prefix
        
        Returns:
            New value after increment
        """
        full_key = self._make_key(key, prefix)
        
        try:
            if self.use_redis:
                return self.redis_client.incrby(full_key, amount)
            else:
                current = self.memory_cache.get(full_key, 0)
                new_value = current + amount
                self.memory_cache[full_key] = new_value
                return new_value
        except Exception as e:
            logger.error(f"Cache increment error for {full_key}: {e}")
            return None
    
    def clear_all(self, prefix: str = "cache") -> bool:
        """
        Clear all keys with given prefix
        
        Args:
            prefix: Key namespace prefix
        
        Returns:
            True if successful
        """
        try:
            if self.use_redis:
                pattern = f"{prefix}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} keys from Redis cache")
            else:
                prefix_str = f"{prefix}:"
                keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(prefix_str)]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                logger.info(f"Cleared {len(keys_to_delete)} keys from memory cache")
            
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'backend': 'redis' if self.use_redis else 'memory',
            'connected': self.use_redis
        }
        
        try:
            if self.use_redis:
                info = self.redis_client.info()
                stats.update({
                    'redis_version': info.get('redis_version'),
                    'used_memory': info.get('used_memory_human'),
                    'total_keys': info.get('db0', {}).get('keys', 0),
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0)
                })
                
                if stats['hits'] + stats['misses'] > 0:
                    stats['hit_rate'] = stats['hits'] / (stats['hits'] + stats['misses']) * 100
            else:
                stats['total_keys'] = len(self.memory_cache)
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
        
        return stats


def cached(ttl: int = 3600, prefix: str = "cache", key_func=None):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        prefix: Cache key prefix
        key_func: Custom function to generate cache key
    
    Example:
        @cached(ttl=300, prefix="jobs")
        def get_job_listings(category):
            return expensive_database_query(category)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: hash function name + arguments
                key_data = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cache = get_cache_service()
            if cache:
                cached_value = cache.get(cache_key, prefix)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {func.__name__}")
                    return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            
            if cache:
                cache.set(cache_key, result, ttl, prefix)
                logger.debug(f"Cached result: {func.__name__}")
            
            return result
        
        return wrapper
    return decorator


# Global singleton
_cache_service = None


def get_cache_service() -> Optional[CacheService]:
    """Get global cache service instance"""
    return _cache_service


def init_cache_service(redis_url: str = None, default_ttl: int = 3600) -> CacheService:
    """Initialize global cache service"""
    global _cache_service
    _cache_service = CacheService(redis_url, default_ttl)
    return _cache_service
