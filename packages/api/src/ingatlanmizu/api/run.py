import uvicorn
from datetime import date
from fastapi import FastAPI
from ingatlanmizu.core.config import settings
from ingatlanmizu.api.selectors import fetch_market_indicators_monthly, fetch_market_monthly_by_county, fetch_market_monthly_by_city

app = FastAPI()

@app.get("/market-monthly-by-county")
def market_monthly_by_county(month_start: date):
    return fetch_market_monthly_by_county(
        month_start=month_start,
    )

@app.get("/market-monthly-by-city")
def market_monthly_by_city(month_start: date, county: str|None = None):
    return fetch_market_monthly_by_city(
        month_start=month_start,
        county=county,
    )
    
@app.get("/market-indicators-monthly")
def market_indicators_monthly(month_start: date):
    return fetch_market_indicators_monthly(
        month_start=month_start,
    )

def main():
    uvicorn.run(
        "ingatlanmizu.api.run:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.environment == 'local' else False,
    )