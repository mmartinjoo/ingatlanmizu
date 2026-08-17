from ingatlanmizu.core.db import connection
import pandas as pd
from datetime import datetime
from ingatlanmizu.indicators.sources.mnb.extract import fetch as fetch_mnb
from ingatlanmizu.indicators.sources.mnb.parse import parse as parse_mnb
from ingatlanmizu.indicators.sources.mnb.load import load as load_mnb
from ingatlanmizu.indicators.sources.bankmonitor.extract import fetch as fetch_bankmonitor
from ingatlanmizu.indicators.sources.bankmonitor.parse import parse as parse_bankmonitor
from ingatlanmizu.indicators.sources.bankmonitor.load import load as load_bankmonitor

def main():
    _ingest_bankmonitor_loans()
    _ingest_mnb_base_rates()
    
def _ingest_mnb_base_rates():
    print("ingesting MNB base rates")
    df: pd.DataFrame = fetch_mnb()
    df = parse_mnb(df)
    load_mnb(df)
    print("ingested MNB base rates")
    
def _ingest_bankmonitor_loans():
    print("ingesting bankmonitor loans")
    data = fetch_bankmonitor()
    loans = parse_bankmonitor(data=data, now=datetime.now())
    load_bankmonitor(loans)
    print("ingested bankmonitor loans")