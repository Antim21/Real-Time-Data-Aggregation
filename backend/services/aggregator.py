import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from statistics import median

from services.apis import exchangerate_api, frankfurter, fawazahmed
from services.cache import rate_cache
from models import FreshnessStatus

# Currency metadata for display
CURRENCY_INFO = {
    "USD": "US Dollar",
    "EUR": "Euro", 
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "CAD": "Canadian Dollar",
    "AUD": "Australian Dollar",
    "CHF": "Swiss Franc",
    "INR": "Indian Rupee",
    "CNY": "Chinese Yuan",
    "MXN": "Mexican Peso"
}

TARGET_CURRENCIES = list(CURRENCY_INFO.keys())

# Determine freshness based on data age
def calculate_freshness(last_updated: datetime) -> FreshnessStatus:
    age = datetime.utcnow() - last_updated
    
    if age < timedelta(minutes=5):
        return FreshnessStatus.FRESH
    elif age < timedelta(minutes=30):
        return FreshnessStatus.RECENT
    else:
        return FreshnessStatus.STALE

# Resolve conflicting rates from multiple APIs
def resolve_conflicts(api_results: List[Dict], currency: str) -> Optional[float]:
    rates = []
    
    for result in api_results:
        if result and currency in result.get("rates", {}):
            rate = result["rates"][currency]
            if isinstance(rate, (int, float)) and rate > 0:
                rates.append(rate)
    
    if not rates:
        return None
    
    if len(rates) == 1:
        return rates[0]
    
    # Use median to handle outliers from stale sources
    return median(rates)


async def fetch_all_rates(base: str = "USD") -> Tuple[Dict, int, int]:
    # Parallel API calls for speed
    results = await asyncio.gather(
        exchangerate_api.fetch_rates(base),
        frankfurter.fetch_rates(base),
        fawazahmed.fetch_rates(base),
        return_exceptions=True
    )
    
    valid_results = [r for r in results if r and not isinstance(r, Exception)]
    sources_available = 3
    sources_used = len(valid_results)
    
    if sources_used == 0:
        return {}, 0, sources_available
    
    aggregated_rates = {}
    
    for currency in TARGET_CURRENCIES:
        if currency == base:
            aggregated_rates[currency] = {
                "code": currency,
                "name": CURRENCY_INFO.get(currency, currency),
                "rate": 1.0,
                "inverse_rate": 1.0
            }
        else:
            rate = resolve_conflicts(valid_results, currency)
            if rate:
                aggregated_rates[currency] = {
                    "code": currency,
                    "name": CURRENCY_INFO.get(currency, currency),
                    "rate": round(rate, 6),
                    "inverse_rate": round(1 / rate, 6)
                }
    
    return aggregated_rates, sources_used, sources_available

# Main function with cache-first strategy
async def get_exchange_rates(base: str = "USD") -> Dict:
    cache_key = f"rates_{base}"
    
    # Check cache first
    cached = rate_cache.get(cache_key)
    if cached and not cached["is_stale"]:
        return {
            "base": base,
            "rates": cached["data"]["rates"],
            "last_updated": cached["cached_at"],
            "freshness": calculate_freshness(cached["cached_at"]),
            "sources_used": cached["data"]["sources_used"],
            "sources_available": cached["data"]["sources_available"],
            "is_cached": True,
            "cache_age_seconds": cached["age_seconds"],
            "message": None
        }
    # Fetch fresh data from APIs
    rates, sources_used, sources_available = await fetch_all_rates(base)
    
    if sources_used > 0 and rates:
        now = datetime.utcnow()
        
        rate_cache.set(cache_key, {
            "rates": rates,
            "sources_used": sources_used,
            "sources_available": sources_available
        })
        
        return {
            "base": base,
            "rates": rates,
            "last_updated": now,
            "freshness": FreshnessStatus.FRESH,
            "sources_used": sources_used,
            "sources_available": sources_available,
            "is_cached": False,
            "cache_age_seconds": 0,
            "message": None
        }
    
    # Fallback to stale cache if APIs fail
    stale_cached = rate_cache.get_stale(cache_key)
    if stale_cached:
        return {
            "base": base,
            "rates": stale_cached["data"]["rates"],
            "last_updated": stale_cached["cached_at"],
            "freshness": FreshnessStatus.STALE,
            "sources_used": 0,
            "sources_available": sources_available,
            "is_cached": True,
            "cache_age_seconds": stale_cached["age_seconds"],
            "message": "Using cached data - live rates temporarily unavailable"
        }
    
    return {
        "base": base,
        "rates": {},
        "last_updated": datetime.utcnow(),
        "freshness": FreshnessStatus.STALE,
        "sources_used": 0,
        "sources_available": sources_available,
        "is_cached": False,
        "cache_age_seconds": None,
        "message": "Rates temporarily unavailable. Please try again shortly."
    }
