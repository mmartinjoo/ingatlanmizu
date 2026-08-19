from ast import main
from datetime import date
from ingatlanmizu.core.db import pool
from ingatlanmizu.api.models import MarketMonthlyByCounty, MarketMonthlyByCity, MarketIndicatorsMonthly, MarketMonthlyChangeByCounty

def fetch_market_months() -> list[date]:
    """Months that actually have county data, newest first."""
    with pool().connection() as conn:
        rows = conn.execute("""
            select distinct month_start
            from gold.mart_market_monthly_by_county
            order by month_start desc
        """).fetchall()

        return [row[0] for row in rows]

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
    
def fetch_market_monthly_by_city(
    month_start: date, 
    county: str|None = None,
    city: str|None = None,
) -> list[MarketMonthlyByCity]:
    results = []
    with pool().connection() as conn:
        q = """
            select 
                month_start, 
                city, 
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
            from gold.mart_market_monthly_by_city
            where month_start = %s
        """
        
        values = (month_start,)
        
        if county is not None:
            q += "\nand county = %s"
            values = (month_start, county,)
            
            if city is not None:
                q += "\nand city = %s"
                values = (month_start, county, city,)
                
        rows = conn.execute(q, values).fetchall()
        
        for row in rows:
            results.append(MarketMonthlyByCity(
                month_start=row[0],
                city=row[1],
                county=row[2],
                main_type=row[3],
                listing_count=row[4],
                new_build_count=row[5],
                old_build_count=row[6],
                unknown_build_count=row[7],
                median_price_per_sqm=row[8],
                median_year_of_building=row[9],
                median_condition_score=row[10],
                new_build_ratio=row[11],
            ))
            
        return results
    
def fetch_market_indicators_monthly(month_start: date) -> MarketIndicatorsMonthly | None:
    """None when the month has no indicators - absence, not zeroes."""
    with pool().connection() as conn:
        row = conn.execute("""
            select 
                month_start, 
                base_rate, 
                inflation, 
                median_apr, 
                lowest_apr, 
                highest_apr, 
                median_monthly_installment, 
                lowest_monthly_installment, 
                highest_monthly_installment
            from gold.mart_market_indicators_monthly
            where month_start = %s
        """, (month_start,)).fetchone()
        
        if row is None:
            return None
        
        return MarketIndicatorsMonthly(
            month_start=row[0],
            base_rate=row[1],
            inflation=row[2],
            median_apr=row[3],
            lowest_apr=row[4],
            highest_apr=row[5],
            median_monthly_installment=row[6],
            lowest_monthly_installment=row[7],
            highest_monthly_installment=row[8],
        )
    
def fetch_cities(county: str) -> list[str]:
    with pool().connection() as conn:
        rows = conn.execute("""
            select distinct city
            from gold.mart_listings_current 
            where county = %s    
        """, (county,)).fetchall()
        
    return [row[0] for row in rows]

def fetch_market_monthly_change_by_county(
    month_start: date, 
    county: str,
    main_type: str,
) -> list[MarketMonthlyChangeByCounty]:
    with pool().connection() as conn:
        rows = conn.execute("""
            select
                month_start,
                county,
                main_type,
                current_median_price_per_sqm,
                change_pct
            from gold.mart_market_monthly_change_by_county
            where county = %s
            and main_type = %s
            and month_start between %s - interval '11 months' and %s
            order by month_start asc           
        """, (county, main_type, month_start, month_start,)).fetchall()
        
        results = []
        for row in rows:
            results.append(MarketMonthlyChangeByCounty(
                month_start=row[0],
                county=row[1],
                main_type=row[2],
                current_median_price_per_sqm=row[3],
                change_pct=row[4],
            ))
            
        return results
    
def fetch_overall_listing_count() -> int:
    with pool().connection() as conn:
        row = conn.execute("select count(*) from gold.mart_listings_current").fetchone()
        return row[0]