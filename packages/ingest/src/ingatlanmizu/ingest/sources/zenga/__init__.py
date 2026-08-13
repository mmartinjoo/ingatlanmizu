from ingatlanmizu.ingest.sources.base import Source
from ingatlanmizu.ingest.sources.zenga.extract import discover, fetch_listing
from ingatlanmizu.ingest.sources.zenga.parse import parse
from ingatlanmizu.ingest.sources.zenga.load import load, hash_payload, record_observation

SEED_URLS = [
    "https://www.zenga.hu/szombathely+elado+haz",
    "https://www.zenga.hu/zalaegerszeg+elado+haz",
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