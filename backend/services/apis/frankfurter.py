import httpx
from typing import Optional, Dict
from datetime import datetime


async def fetch_rates(base: str = "USD") -> Optional[Dict]:
    """
    Fetch rates from Frankfurter API.
    https://www.frankfurter.app/
    
    Free, no API key needed, backed by European Central Bank data.
    Note: ECB doesn't publish rates for USD as base, so we may need to convert.
    """
    url = f"https://api.frankfurter.app/latest?from={base}"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Frankfurter returns rates relative to base
            rates = data.get("rates", {})
            
            # Add base currency with rate 1.0
            rates[base] = 1.0
            
            return {
                "source": "frankfurter",
                "base": base,
                "rates": rates,
                "fetched_at": datetime.utcnow(),
                "api_updated": data.get("date", "")
            }
            
    except Exception as e:
        print(f"Frankfurter API error: {e}")
        return None
