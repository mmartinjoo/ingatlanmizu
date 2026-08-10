from ingatlanmizu.ingest.sources.base import Source
from ingatlanmizu.ingest.sources.zenga.extract import SEED_URLS, discover, fetch_listing
from ingatlanmizu.ingest.sources.zenga.parse import parse
from ingatlanmizu.ingest.sources.zenga.load import load, hash_payload


SOURCE = Source(
    name="zenga",
    seed_urls=SEED_URLS,
    discover=discover,
    fetch_listing=fetch_listing,
    parse=parse,
    load=load,
    hash_payload=hash_payload,
)