from ingatlanmizu.ingest.sources.base import Source
from ingatlanmizu.ingest.sources.zenga import SOURCE as ZENGA

SOURCES: dict[str, Source] = {s.name: s for s in (ZENGA,)}

def get_source(name: str) -> Source:
    try:
        return SOURCES[name]
    except KeyError:
        raise ValueError(f"unknown source {name}; known: {SOURCES}")