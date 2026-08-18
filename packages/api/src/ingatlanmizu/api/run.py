import uvicorn
from fastapi import FastAPI
from ingatlanmizu.core.config import settings
from ingatlanmizu.api.selectors import fetch_market_monthly_by_county

app = FastAPI()

@app.get("/market-monthly-by-county")
def market_monthly_by_county():
    return fetch_market_monthly_by_county("2026-08-01")

def main():
    uvicorn.run(
        "ingatlanmizu.api.run:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.environment == 'local' else False,
    )