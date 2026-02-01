from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import threading


class RateCache:
    """
    Simple in-memory cache with TTL support.
    Thread-safe for concurrent access.
    """
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._ttl = timedelta(seconds=ttl_seconds)
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached value if exists and not expired.
        Returns tuple of (data, age_seconds, is_stale)
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            cached_time = self._timestamps[key]
            age = datetime.utcnow() - cached_time
            is_stale = age > self._ttl
            
            return {
                "data": self._cache[key],
                "cached_at": cached_time,
                "age_seconds": int(age.total_seconds()),
                "is_stale": is_stale
            }
    
    def set(self, key: str, value: Any) -> None:
        """Store value in cache with current timestamp"""
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = datetime.utcnow()
    
    def get_stale(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached value even if stale (for fallback scenarios).
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            cached_time = self._timestamps[key]
            age = datetime.utcnow() - cached_time
            
            return {
                "data": self._cache[key],
                "cached_at": cached_time,
                "age_seconds": int(age.total_seconds()),
                "is_stale": True
            }
    
    def clear(self) -> None:
        """Clear all cached data"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()


# Global cache instance
rate_cache = RateCache(ttl_seconds=300)  # 5 minute TTL
