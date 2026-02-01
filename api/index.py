from flask import Flask, request, jsonify
from datetime import datetime
import requests
from statistics import median

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

TARGET_CURRENCIES = list(CURRENCY_INFO.keys())


def fetch_exchangerate_api(base):
    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        response = requests.get(url, timeout=8, headers={'User-Agent': 'CurrencyApp/1.0'})
        if response.status_code == 200:
            data = response.json()
            if data.get("result") == "success":
                return data.get("rates", {})
    except Exception as e:
        print(f"ExchangeRate-API error: {e}")
    return None


def fetch_frankfurter(base):
    try:
        url = f"https://api.frankfurter.app/latest?from={base}"
        response = requests.get(url, timeout=8, headers={'User-Agent': 'CurrencyApp/1.0'})
        if response.status_code == 200:
            data = response.json()
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
        response = requests.get(url, timeout=8, headers={'User-Agent': 'CurrencyApp/1.0'})
        if response.status_code == 200:
            data = response.json()
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
    # Try each API one by one
    results = []
    
    result1 = fetch_exchangerate_api(base)
    if result1:
        results.append(result1)
    
    result2 = fetch_frankfurter(base)
    if result2:
        results.append(result2)
    
    result3 = fetch_fawazahmed(base)
    if result3:
        results.append(result3)
    
    sources_used = len(results)
    
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
            rate = resolve_conflicts(results, currency)
            if rate:
                aggregated_rates[currency] = {
                    "code": currency,
                    "name": CURRENCY_INFO.get(currency, currency),
                    "rate": round(rate, 6),
                    "inverse_rate": round(1 / rate, 6)
                }
    
    return aggregated_rates, sources_used


@app.route('/api/rates', methods=['GET', 'OPTIONS'])
def rates():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    
    base = request.args.get('base', 'USD').upper()
    result = get_exchange_rates(base)
    
    if not result or not result[0]:
        response = jsonify({
            "error": True,
            "message": "Rates temporarily unavailable",
            "retry_after_seconds": 30
        })
        response.status_code = 503
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    rates_data, sources_used = result
    response = jsonify({
        "base": base,
        "rates": rates_data,
        "last_updated": datetime.utcnow().isoformat(),
        "freshness": "fresh",
        "sources_used": sources_used,
        "sources_available": 3,
        "is_cached": False,
        "cache_age_seconds": 0,
        "message": None
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


# For local testing
if __name__ == '__main__':
    app.run(debug=True, port=5000)
