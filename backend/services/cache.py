from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import threading


# Thread-safe in-memory cache with TTL
class RateCache:
    def __init__(self, ttl_seconds: int = 300):  # 5-minute default TTL
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._ttl = timedelta(seconds=ttl_seconds)
        self._lock = threading.Lock()  # Thread safety
    # Get cached value with staleness info
    def get(self, key: str) -> Optional[Dict[str, Any]]:
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
    # Store value with current timestamp
    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = datetime.utcnow()
    # Get stale cache for fallback scenarios
    def get_stale(self, key: str) -> Optional[Dict[str, Any]]:
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
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()

# Global cache instance
rate_cache = RateCache(ttl_seconds=300)
