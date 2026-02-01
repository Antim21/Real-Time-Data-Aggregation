from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from models import ExchangeRateResponse, ErrorResponse
from services.aggregator import get_exchange_rates

app = FastAPI(
    title="Currency Exchange Rate API",
    description="Real-time currency exchange rates aggregated from multiple sources",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Currency Exchange Rate API",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/rates", response_model=ExchangeRateResponse)
async def get_rates(
    base: str = Query(
        default="USD",
        description="Base currency code (e.g., USD, EUR, GBP)",
        min_length=3,
        max_length=3
    )
):
    """
    Get current exchange rates for major currencies.
    
    - **base**: The base currency to get rates for (default: USD)
    
    Returns exchange rates with freshness indicator and source information.
    Data is aggregated from multiple public APIs for reliability.
    """
    base = base.upper()
    
    # Get aggregated rates
    result = await get_exchange_rates(base)
    
    # Handle case where no rates available at all
    if not result["rates"]:
        return JSONResponse(
            status_code=503,
            content={
                "error": True,
                "message": result.get("message", "Rates temporarily unavailable"),
                "retry_after_seconds": 30
            }
        )
    
    return ExchangeRateResponse(
        base=result["base"],
        rates=result["rates"],
        last_updated=result["last_updated"],
        freshness=result["freshness"],
        sources_used=result["sources_used"],
        sources_available=result["sources_available"],
        is_cached=result["is_cached"],
        cache_age_seconds=result.get("cache_age_seconds"),
        message=result.get("message")
    )


@app.get("/health")
async def health_check():
    """Detailed health check with API status"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "apis": {
            "exchangerate_api": "configured",
            "frankfurter": "configured", 
            "fawazahmed": "configured"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
