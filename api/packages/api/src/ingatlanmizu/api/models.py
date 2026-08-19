from dataclasses import dataclass
from datetime import date

@dataclass
class MarketMonthlyByCounty():
    month_start: date
    county: str
    main_type: str
    listing_count: int
    new_build_count: int
    old_build_count: int
    unknown_build_count: int
    median_price_per_sqm: int
    median_year_of_building: int
    median_condition_score: int
    new_build_ratio: float
    
@dataclass
class MarketMonthlyByCity():
    month_start: date
    county: str
    city: str
    main_type: str
    listing_count: int
    new_build_count: int
    old_build_count: int
    unknown_build_count: int
    median_price_per_sqm: int
    median_year_of_building: int
    median_condition_score: int
    new_build_ratio: float
    
@dataclass
class MarketIndicatorsMonthly():
    month_start: date 
    base_rate: float 
    inflation: float 
    median_apr: float 
    lowest_apr: float 
    highest_apr: float 
    median_monthly_installment: int 
    lowest_monthly_installment: int 
    highest_monthly_installment: int 
    
@dataclass
class MarketMonthlyChangeByCounty():
    month_start: date
    county: str
    main_type: str
    current_median_price_per_sqm: int
    change_pct: float