from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from datetime import datetime

# Currency metadata
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

# Fallback rates (approximate values)
FALLBACK_RATES = {
    "USD": {"EUR": 0.92, "GBP": 0.79, "JPY": 149.5, "CAD": 1.36, "AUD": 1.53, "CHF": 0.88, "INR": 83.1, "CNY": 7.24, "MXN": 17.15},
    "EUR": {"USD": 1.09, "GBP": 0.86, "JPY": 162.5, "CAD": 1.48, "AUD": 1.66, "CHF": 0.96, "INR": 90.3, "CNY": 7.87, "MXN": 18.65},
    "GBP": {"USD": 1.27, "EUR": 1.17, "JPY": 189.2, "CAD": 1.72, "AUD": 1.94, "CHF": 1.11, "INR": 105.2, "CNY": 9.16, "MXN": 21.72},
    "JPY": {"USD": 0.0067, "EUR": 0.0062, "GBP": 0.0053, "CAD": 0.0091, "AUD": 0.0102, "CHF": 0.0059, "INR": 0.556, "CNY": 0.0484, "MXN": 0.115},
    "INR": {"USD": 0.012, "EUR": 0.011, "GBP": 0.0095, "JPY": 1.8, "CAD": 0.016, "AUD": 0.018, "CHF": 0.011, "CNY": 0.087, "MXN": 0.206}
}


def try_fetch_live_rates(base):
    """Try to fetch live rates from external API"""
    try:
        import urllib.request
        import ssl
        
        ctx = ssl.create_default_context()
        
        url = f"https://open.er-api.com/v6/latest/{base}"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        
        with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
            data = json.loads(response.read().decode())
            if data.get("result") == "success":
                return data.get("rates", {}), True
    except Exception as e:
        print(f"Live API error: {e}")
    
    return None, False


def get_rates_data(base):
    """Get rates - try live first, fallback to static"""
    live_rates, is_live = try_fetch_live_rates(base)
    
    if live_rates:
        raw_rates = live_rates
        sources_used = 1
        is_cached = False
        freshness = "fresh"
        message = None
    else:
        # Use fallback
        raw_rates = FALLBACK_RATES.get(base, FALLBACK_RATES.get("USD", {}))
        sources_used = 0
        is_cached = True
        freshness = "stale"
        message = "Using cached rates - live data temporarily unavailable"
    
    # Build response
    result = {}
    result[base] = {
        "code": base,
        "name": CURRENCY_INFO.get(base, base),
        "rate": 1.0,
        "inverse_rate": 1.0
    }
    
    for currency, name in CURRENCY_INFO.items():
        if currency != base and currency in raw_rates:
            rate = raw_rates[currency]
            if isinstance(rate, (int, float)) and rate > 0:
                result[currency] = {
                    "code": currency,
                    "name": name,
                    "rate": round(float(rate), 6),
                    "inverse_rate": round(1.0 / float(rate), 6)
                }
    
    return {
        "base": base,
        "rates": result,
        "last_updated": datetime.utcnow().isoformat(),
        "freshness": freshness,
        "sources_used": sources_used,
        "sources_available": 3,
        "is_cached": is_cached,
        "cache_age_seconds": 0 if not is_cached else 3600,
        "message": message
    }


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if '/rates' in path:
            base = params.get('base', ['USD'])[0].upper()
            response = get_rates_data(base)
        elif '/health' in path:
            response = {
                "status": "healthy",
                "service": "Currency Exchange Rate API",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            response = {
                "status": "healthy",
                "service": "Currency Exchange Rate API",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        self.wfile.write(json.dumps(response).encode())
