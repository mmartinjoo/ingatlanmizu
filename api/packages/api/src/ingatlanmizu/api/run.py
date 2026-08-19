import uvicorn
from datetime import date
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ingatlanmizu.core.config import settings
from ingatlanmizu.api.selectors import fetch_market_indicators_monthly, fetch_market_monthly_by_county, fetch_market_monthly_by_city, fetch_market_months, fetch_cities, fetch_market_monthly_change_by_county, fetch_overall_listing_count

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/market-months")
def market_months():
    return fetch_market_months()

@app.get("/api/counties/{county}/cities")
def cities(county: str):
    return fetch_cities(county)

@app.get("/api/market-monthly-by-county")
def market_monthly_by_county(month_start: date):
    return fetch_market_monthly_by_county(
        month_start=month_start,
    )

@app.get("/api/market-monthly-by-city")
def market_monthly_by_city(
    month_start: date, 
    county: str|None = None,
    city: str|None = None,
):
    return fetch_market_monthly_by_city(
        month_start=month_start,
        county=county,
        city=city,
    )
    
@app.get("/api/market-indicators-monthly")
def market_indicators_monthly(month_start: date):
    return fetch_market_indicators_monthly(
        month_start=month_start,
    )
    
@app.get("/api/market-monthly-change-by-county/{county}")
def market_monthy_change_by_county(month_start: date, county: str, main_type: str):
    return fetch_market_monthly_change_by_county(
        month_start=month_start,
        county=county,
        main_type=main_type,
    )
    
@app.get("/api/listing-count")
def listing_count():
    count = fetch_overall_listing_count()
    return {
        "count": count,
    }

def main():
    uvicorn.run(
        "ingatlanmizu.api.run:app",
        host="0.0.0.0",
        port=80,
        reload=True if settings.environment == 'local' else False,
    )