from ingatlanmizu.core.db import connection
import pandas as pd
from ingatlanmizu.indicators.sources.mnb.extract import fetch
from ingatlanmizu.indicators.sources.mnb.parse import parse
from ingatlanmizu.indicators.sources.mnb.load import load

def main():
    _ingest_mnb_base_rates()
    
def _ingest_mnb_base_rates():
    print("ingesting MNB base rates")
    df: pd.DataFrame = fetch()
    df = parse(df)
    load(df)
    print("ingested MNB base rates")