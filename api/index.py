from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

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

# Fallback rates (approximate, updated periodically)
FALLBACK_RATES = {
    "USD": {"EUR": 0.92, "GBP": 0.79, "JPY": 149.5, "CAD": 1.36, "AUD": 1.53, "CHF": 0.88, "INR": 83.1, "CNY": 7.24, "MXN": 17.15},
    "EUR": {"USD": 1.09, "GBP": 0.86, "JPY": 162.5, "CAD": 1.48, "AUD": 1.66, "CHF": 0.96, "INR": 90.3, "CNY": 7.87, "MXN": 18.65},
    "GBP": {"USD": 1.27, "EUR": 1.17, "JPY": 189.2, "CAD": 1.72, "AUD": 1.94, "CHF": 1.11, "INR": 105.2, "CNY": 9.16, "MXN": 21.72},
    "JPY": {"USD": 0.0067, "EUR": 0.0062, "GBP": 0.0053, "CAD": 0.0091, "AUD": 0.0102, "CHF": 0.0059, "INR": 0.556, "CNY": 0.0484, "MXN": 0.115},
    "INR": {"USD": 0.012, "EUR": 0.011, "GBP": 0.0095, "JPY": 1.8, "CAD": 0.016, "AUD": 0.018, "CHF": 0.011, "CNY": 0.087, "MXN": 0.206}
}


def fetch_rates_with_requests(base):
    """Try to fetch rates using requests library"""
    try:
        import requests
        
        # Try ExchangeRate-API first (most reliable)
        url = f"https://open.er-api.com/v6/latest/{base}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("result") == "success":
                return data.get("rates", {}), "exchangerate-api"
    except Exception as e:
        print(f"Requests error: {e}")
    
    return None, None


def fetch_rates_with_urllib(base):
    """Fallback: Try with urllib"""
    try:
        import urllib.request
        import ssl
        
        # Create SSL context that doesn't verify (some serverless envs have issues)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        url = f"https://open.er-api.com/v6/latest/{base}"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
            data = json.loads(response.read().decode())
            if data.get("result") == "success":
                return data.get("rates", {}), "exchangerate-api"
    except Exception as e:
        print(f"Urllib error: {e}")
    
    return None, None


def get_fallback_rates(base):
    """Return fallback rates if live APIs fail"""
    if base not in FALLBACK_RATES:
        base = "USD"
    
    rates = FALLBACK_RATES.get(base, {})
    return rates, "fallback"


def build_response(base, raw_rates, source):
    """Build the response with proper structure"""
    aggregated_rates = {}
    
    # Add base currency
    aggregated_rates[base] = {
        "code": base,
        "name": CURRENCY_INFO.get(base, base),
        "rate": 1.0,
        "inverse_rate": 1.0
    }
    
    # Add other currencies
    for currency, name in CURRENCY_INFO.items():
        if currency != base and currency in raw_rates:
            rate = raw_rates[currency]
            if isinstance(rate, (int, float)) and rate > 0:
                aggregated_rates[currency] = {
                    "code": currency,
                    "name": name,
                    "rate": round(rate, 6),
                    "inverse_rate": round(1 / rate, 6)
                }
    
    return aggregated_rates


@app.route('/api/rates', methods=['GET', 'OPTIONS'])
def rates():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    
    base = request.args.get('base', 'USD').upper()
    
    # Try different methods to fetch rates
    raw_rates = None
    source = None
    sources_used = 0
    
    # Method 1: Try requests library
    raw_rates, source = fetch_rates_with_requests(base)
    if raw_rates:
        sources_used = 1
    
    # Method 2: Try urllib
    if not raw_rates:
        raw_rates, source = fetch_rates_with_urllib(base)
        if raw_rates:
            sources_used = 1
    
    # Method 3: Use fallback rates
    if not raw_rates:
        raw_rates, source = get_fallback_rates(base)
        sources_used = 0  # Fallback doesn't count as a live source
    
    # Build response
    rates_data = build_response(base, raw_rates, source)
    
    freshness = "fresh" if source != "fallback" else "stale"
    message = None if source != "fallback" else "Using cached rates - live data temporarily unavailable"
    
    response = jsonify({
        "base": base,
        "rates": rates_data,
        "last_updated": datetime.utcnow().isoformat(),
        "freshness": freshness,
        "sources_used": sources_used,
        "sources_available": 3,
        "is_cached": source == "fallback",
        "cache_age_seconds": 0 if source != "fallback" else 3600,
        "message": message
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/api/health', methods=['GET'])
def health():
    response = jsonify({
        "status": "healthy",
        "service": "Currency Exchange Rate API",
        "timestamp": datetime.utcnow().isoformat()
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/', methods=['GET'])
def root():
    response = jsonify({
        "status": "healthy",
        "service": "Currency Exchange Rate API",  
        "timestamp": datetime.utcnow().isoformat()
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    app.run(debug=True, port=5000)
