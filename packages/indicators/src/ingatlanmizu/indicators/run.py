from ingatlanmizu.core.db import connection
import pandas as pd
from ingatlanmizu.indicators.sources.mnb.extract import fetch as fetch_mnb
from ingatlanmizu.indicators.sources.mnb.parse import parse
from ingatlanmizu.indicators.sources.mnb.load import load
from ingatlanmizu.indicators.sources.bankmonitor.extract import fetch as fetch_bankmonitor

def main():
    _ingest_bankmonitor_loans()
    # _ingest_mnb_base_rates()
    
def _ingest_mnb_base_rates():
    print("ingesting MNB base rates")
    df: pd.DataFrame = fetch_mnb()
    df = parse(df)
    load(df)
    print("ingested MNB base rates")
    
def _ingest_bankmonitor_loans():
    print("bankmonitor")
    fetch_bankmonitor()