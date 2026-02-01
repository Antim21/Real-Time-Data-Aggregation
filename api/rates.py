import json
from datetime import datetime
import urllib.request
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


def fetch_exchangerate_api(base):
    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("result") == "success":
                return data.get("rates", {})
    except Exception as e:
        print(f"ExchangeRate-API error: {e}")
    return None


def fetch_frankfurter(base):
    try:
        url = f"https://api.frankfurter.app/latest?from={base}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            rates = data.get("rates", {})
            rates[base] = 1.0
            return rates
    except Exception as e:
        print(f"Frankfurter API error: {e}")
    return None


def fetch_fawazahmed(base):
    try:
        base_lower = base.lower()
        url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base_lower}.json"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            raw_rates = data.get(base_lower, {})
            return {k.upper(): v for k, v in raw_rates.items() if isinstance(v, (int, float))}
    except Exception as e:
        print(f"Fawaz Ahmed API error: {e}")
    return None


def resolve_conflicts(api_results, currency):
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


def get_exchange_rates(base):
    results = [
        fetch_exchangerate_api(base),
        fetch_frankfurter(base),
        fetch_fawazahmed(base)
    ]
    
    valid_results = [r for r in results if r is not None]
    sources_used = len(valid_results)
    
    if sources_used == 0:
        return None, 0
    
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


def handler(request):
    from urllib.parse import parse_qs, urlparse
    
    # Parse query parameters
    parsed = urlparse(request.url if hasattr(request, 'url') else '/?base=USD')
    params = parse_qs(parsed.query)
    base = params.get('base', ['USD'])[0].upper()
    
    # Get rates
    result = get_exchange_rates(base)
    rates = result[0] if result else None
    sources_used = result[1] if result else 0
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': '*'
    }
    
    if not rates:
        return {
            'statusCode': 503,
            'headers': headers,
            'body': json.dumps({
                "error": True,
                "message": "Rates temporarily unavailable",
                "retry_after_seconds": 30
            })
        }
    
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
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(response)
    }
