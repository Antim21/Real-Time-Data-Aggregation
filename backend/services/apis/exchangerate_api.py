import httpx
from typing import Optional, Dict
from datetime import datetime


async def fetch_rates(base: str = "USD") -> Optional[Dict]:
    """
    Fetch rates from ExchangeRate-API (free tier).
    https://www.exchangerate-api.com/
    
    Free tier: 1500 requests/month
    """
    url = f"https://open.er-api.com/v6/latest/{base}"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if data.get("result") != "success":
                return None
            
            return {
                "source": "exchangerate-api",
                "base": base,
                "rates": data.get("rates", {}),
                "fetched_at": datetime.utcnow(),
                "api_updated": data.get("time_last_update_utc", "")
            }
            
    except Exception as e:
        print(f"ExchangeRate-API error: {e}")
        return None
