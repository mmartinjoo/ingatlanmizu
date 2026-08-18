from datetime import date
from ingatlanmizu.core.db import pool
from ingatlanmizu.api.models import MarketMonthlyByCounty, MarketMonthlyByCity, MarketIndicatorsMonthly

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
    
def fetch_market_monthly_by_city(month_start: date, county: str|None = None) -> list[MarketMonthlyByCity]:
    results = []
    with pool().connection() as conn:
        if county is not None:
            rows = conn.execute("""
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
                and county = %s
            """, (month_start,county,)).fetchall()
        else:
            rows = conn.execute("""
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
            """, (month_start,)).fetchall()
        
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
    
def fetch_market_indicators_monthly(month_start: date) -> MarketIndicatorsMonthly:
    with pool().connection() as conn:
        exists = conn.execute("""
            select exists (
                select 1
                from gold.mart_market_indicators_monthly
                where month_start = %s
            )                      
        """, (month_start,)).fetchone()
        
        if exists[0] is False:
            return MarketIndicatorsMonthly(
                month_start=month_start,
                base_rate=0,
                inflation=0,
                median_apr=0,
                lowest_apr=0,
                highest_apr=0,
                median_monthly_installment=0,
                lowest_monthly_installment=0,
                highest_monthly_installment=0,
            )
        
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
    