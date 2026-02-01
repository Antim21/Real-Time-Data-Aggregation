import httpx
from typing import Optional, Dict
from datetime import datetime


# Fetch rates from Fawaz Ahmed Currency API (CDN-hosted, fast)
async def fetch_rates(base: str = "USD") -> Optional[Dict]:
    base_lower = base.lower()
    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base_lower}.json"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                return None
            
            raw_rates = data.get(base_lower, {})
            # Convert keys to uppercase for consistency
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
