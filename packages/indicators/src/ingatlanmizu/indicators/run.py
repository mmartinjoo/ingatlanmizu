import pandas as pd
from ingatlanmizu.indicators.sources.mnb.fetch import fetch
from ingatlanmizu.indicators.sources.mnb.parse import parse
from ingatlanmizu.indicators.sources.mnb.load import load

def main():
    df: pd.DataFrame = fetch()
    df = parse(df)
    load(df)