import json
from datetime import datetime


def handler(request):
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
    
    response = {
        "status": "healthy",
        "service": "Currency Exchange Rate API",
        "timestamp": datetime.utcnow().isoformat(),
        "apis": {
            "exchangerate_api": "configured",
            "frankfurter": "configured",
            "fawazahmed": "configured"
        }
    }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(response)
    }
