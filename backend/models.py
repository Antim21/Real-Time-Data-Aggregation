from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
from enum import Enum


# Data freshness levels based on age
class FreshnessStatus(str, Enum):
    FRESH = "fresh"      # < 5 minutes
    RECENT = "recent"    # 5-30 minutes
    STALE = "stale"      # > 30 minutes

# Individual currency rate data
class RateData(BaseModel):
    code: str
    name: str
    rate: float
    inverse_rate: float

# API response model for exchange rates
class ExchangeRateResponse(BaseModel):
    base: str
    rates: Dict[str, RateData]
    last_updated: datetime
    freshness: FreshnessStatus
    sources_used: int
    sources_available: int
    is_cached: bool
    cache_age_seconds: Optional[int] = None
    message: Optional[str] = None

# Error response model
class ErrorResponse(BaseModel):
    error: bool = True
    message: str
    retry_after_seconds: Optional[int] = 30
