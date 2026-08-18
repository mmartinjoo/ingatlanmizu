from datetime import date
from ingatlanmizu.core.db import pool
from ingatlanmizu.api.models import MarketMonthlyByCounty

def fetch_market_monthly_by_county(month_start: date) -> list[MarketMonthlyByCounty]:
    results = []
    with pool().connection() as conn:
        rows = conn.execute("""
            select 
                month_start, 
                county, 
                main_type, 
                listing_count, 
                new_build_count, 
                old_build_count, 
                unknown_build_count, 
                median_price_per_sqm, 
                median_year_of_building, 
                median_condition_score, 
                new_build_ratio
            from gold.mart_market_monthly_by_county
            where month_start = %s
        """, (month_start,)).fetchall()
        
        for row in rows:
            results.append(MarketMonthlyByCounty(
                month_start=row[0],
                county=row[1],
                main_type=row[2],
                listing_count=row[3],
                new_build_count=row[4],
                old_build_count=row[5],
                unknown_build_count=row[6],
                median_price_per_sqm=row[7],
                median_year_of_building=row[8],
                median_condition_score=row[9],
                new_build_ratio=row[10],
            ))
            
        return results