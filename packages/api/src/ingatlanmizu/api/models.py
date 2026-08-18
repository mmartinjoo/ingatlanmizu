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