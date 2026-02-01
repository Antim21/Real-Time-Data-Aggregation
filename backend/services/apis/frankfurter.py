import httpx
from typing import Optional, Dict
from datetime import datetime


# Fetch rates from Frankfurter API (ECB data, free)
async def fetch_rates(base: str = "USD") -> Optional[Dict]:
    url = f"https://api.frankfurter.app/latest?from={base}"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                return None
            
            rates = data.get("rates", {})
            rates[base] = 1.0  # Add base currency
            
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
