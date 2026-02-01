# Real-Time Currency Exchange Rate Service

A reliable currency exchange rate aggregation service that fetches data from multiple public APIs with graceful fallbacks, caching, and freshness indicators.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ 
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📁 Project Structure

```
/
├── decisions.md          # Design decisions and reasoning
├── README.md             # This file
├── backend/
│   ├── main.py           # FastAPI application
│   ├── models.py         # Pydantic models
│   ├── requirements.txt  # Python dependencies
│   └── services/
│       ├── aggregator.py # Multi-API aggregation logic
│       ├── cache.py      # In-memory caching
│       └── apis/         # Individual API integrations
│           ├── exchangerate_api.py
│           ├── frankfurter.py
│           └── fawazahmed.py
└── frontend/
    ├── src/
    │   ├── App.jsx       # Main application
    │   ├── App.css       # Styling
    │   └── components/   # React components
    │       ├── RateCard.jsx
    │       ├── RateGrid.jsx
    │       ├── FreshnessIndicator.jsx
    │       └── ErrorState.jsx
    └── package.json
```

## 🔌 API Endpoints

### GET /rates
Returns aggregated exchange rates from multiple sources.

**Query Parameters:**
- `base` (optional): Base currency code (default: "USD")

**Response:**
```json
{
  "base": "USD",
  "rates": {
    "EUR": {
      "code": "EUR",
      "name": "Euro",
      "rate": 0.9234,
      "inverse_rate": 1.0829
    }
  },
  "last_updated": "2024-01-15T10:30:00Z",
  "freshness": "fresh",
  "sources_used": 3,
  "sources_available": 3,
  "is_cached": false,
  "message": null
}
```

### GET /health
Health check endpoint with API status.

## ✨ Features

- **Multi-source aggregation**: Fetches from 3 public APIs in parallel
- **Conflict resolution**: Uses median value when sources disagree
- **Graceful fallbacks**: Serves cached data when APIs fail
- **Freshness indicators**: 🟢 Fresh | 🟡 Recent | 🔴 Stale
- **Auto-refresh**: Frontend polls every 60 seconds
- **5-minute caching**: Reduces API load while maintaining freshness
- **No technical errors**: Users see friendly messages, never raw errors

## 🎨 UI Features

- Premium dark theme with gradient accents
- Responsive design (mobile-friendly)
- Animated freshness indicator
- Loading spinners and skeleton states
- Error recovery with retry button

## 🔧 Configuration

### Cache TTL
Edit `backend/services/cache.py` to change cache duration:
```python
rate_cache = RateCache(ttl_seconds=300)  # 5 minutes
```

### Target Currencies
Edit `backend/services/aggregator.py` to change displayed currencies:
```python
TARGET_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "INR"]
```

### Refresh Interval
Edit `frontend/src/App.jsx` to change auto-refresh:
```javascript
const REFRESH_INTERVAL = 60000  // 60 seconds
```

## 📊 Data Sources

| API | Rate Limit | Notes |
|-----|-----------|-------|
| ExchangeRate-API | 1500/month | Primary source |
| Frankfurter | Unlimited | ECB data |
| Fawaz Ahmed | Unlimited | CDN-hosted |

## 🤝 Contributing

This is a demo project built in 60 minutes. See `decisions.md` for architecture decisions and future improvements.

## 📝 License

MIT
