from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
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
        self.wfile.write(json.dumps(response).encode())
