import httpx
from typing import Optional, Dict
from datetime import datetime


async def fetch_rates(base: str = "USD") -> Optional[Dict]:
    """
    Fetch rates from Fawaz Ahmed's Currency API.
    https://github.com/fawazahmed0/exchange-api
    
    Free, no API key, hosted on GitHub/CDN, very fast.
    """
    base_lower = base.lower()
    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base_lower}.json"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # This API returns rates nested under the base currency
            raw_rates = data.get(base_lower, {})
            
            # Convert to uppercase keys for consistency
            rates = {k.upper(): v for k, v in raw_rates.items() if isinstance(v, (int, float))}
            
            return {
                "source": "fawazahmed",
                "base": base,
                "rates": rates,
                "fetched_at": datetime.utcnow(),
                "api_updated": data.get("date", "")
            }
            
    except Exception as e:
        print(f"Fawaz Ahmed API error: {e}")
        return None
