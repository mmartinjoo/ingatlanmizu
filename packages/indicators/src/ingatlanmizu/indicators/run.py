from ingatlanmizu.indicators.sources.mnb.fetch import fetch
from ingatlanmizu.indicators.sources.mnb.parse import parse

def main():
    df = fetch()
    parse(df)