from ingatlanmizu.ingest.sources.base import Source, SeedUrl
from ingatlanmizu.ingest.sources.zenga.extract import discover, fetch_listing
from ingatlanmizu.ingest.sources.zenga.parse import parse
from ingatlanmizu.ingest.sources.zenga.load import load, hash_payload, record_observation

SEED_URLS = [
    # SeedUrl(county="Vas megye", main_type="Lakás", url="https://www.zenga.hu/vas-megye+elado+lakas"),
    # SeedUrl(county="Vas megye", main_type="Ház", url="https://www.zenga.hu/vas-megye+elado+haz"),
    # SeedUrl(county="Zala megye", main_type="Lakás", url="https://www.zenga.hu/zala-megye+elado+lakas"),
    # SeedUrl(county="Zala megye", main_type="Ház", url="https://www.zenga.hu/zala-megye+elado+haz"),
    SeedUrl(county="Budapest", main_type="Lakás", url="https://www.zenga.hu/budapest-xiii-kerulet+elado+haz"),
]

SOURCE = Source(
    name="zenga",
    seed_urls=SEED_URLS,
    discover=discover,
    fetch_listing=fetch_listing,
    parse=parse,
    load=load,
    hash_payload=hash_payload,
    record_observation=record_observation,
)