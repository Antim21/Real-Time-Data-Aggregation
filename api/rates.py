from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import urllib.request
import urllib.error
from statistics import median


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


def fetch_exchangerate_api(base: str):
    """Fetch rates from ExchangeRate-API"""
    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get("result") == "success":
                return data.get("rates", {})
    except Exception as e:
        print(f"ExchangeRate-API error: {e}")
    return None


def fetch_frankfurter(base: str):
    """Fetch rates from Frankfurter API"""
    try:
        url = f"https://api.frankfurter.app/latest?from={base}"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            rates = data.get("rates", {})
            rates[base] = 1.0
            return rates
    except Exception as e:
        print(f"Frankfurter API error: {e}")
    return None


def fetch_fawazahmed(base: str):
    """Fetch rates from Fawaz Ahmed API"""
    try:
        base_lower = base.lower()
        url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base_lower}.json"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            raw_rates = data.get(base_lower, {})
            return {k.upper(): v for k, v in raw_rates.items() if isinstance(v, (int, float))}
    except Exception as e:
        print(f"Fawaz Ahmed API error: {e}")
    return None


def resolve_conflicts(api_results, currency):
    """Use median to handle conflicting rates"""
    rates = []
    for result in api_results:
        if result and currency in result:
            rate = result[currency]
            if isinstance(rate, (int, float)) and rate > 0:
                rates.append(rate)
    
    if not rates:
        return None
    if len(rates) == 1:
        return rates[0]
    return median(rates)


def get_exchange_rates(base: str):
    """Aggregate rates from multiple APIs"""
    # Fetch from all APIs
    results = [
        fetch_exchangerate_api(base),
        fetch_frankfurter(base),
        fetch_fawazahmed(base)
    ]
    
    valid_results = [r for r in results if r is not None]
    sources_used = len(valid_results)
    
    if sources_used == 0:
        return None, 0
    
    # Aggregate rates
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
    
    return aggregated_rates, sources_used


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        base = params.get('base', ['USD'])[0].upper()
        
        # Get rates
        rates, sources_used = get_exchange_rates(base) or ({}, 0)
        
        if not rates:
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "error": True,
                "message": "Rates temporarily unavailable",
                "retry_after_seconds": 30
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Success response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "base": base,
            "rates": rates,
            "last_updated": datetime.utcnow().isoformat(),
            "freshness": "fresh",
            "sources_used": sources_used,
            "sources_available": 3,
            "is_cached": False,
            "cache_age_seconds": 0,
            "message": None
        }
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
