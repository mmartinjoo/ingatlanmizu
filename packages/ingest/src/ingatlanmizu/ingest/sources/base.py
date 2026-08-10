from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Source:
    name: str
    seed_urls: list[str]
    discover: Callable[[list[str]], list[tuple[str, str]]]  # [seed_urls] -> [(external_id, url)]
    fetch_listing: Callable[[str, str], str]                # (external_id, url) -> content_hash
    parse: Callable[[str], dict[str, str|None]]             # html -> listing dict
    load: Callable[[dict[str, str|None]], None]             # listing dict -> None