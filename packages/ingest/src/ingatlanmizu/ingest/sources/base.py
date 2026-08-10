from dataclasses import dataclass
from typing import Callable, TypeAlias

SourceSpecificListingDict: TypeAlias = dict[str, str|None]
SeedUrl: TypeAlias = str
IngestionRunId: TypeAlias = int
PayloadHash: TypeAlias = str
NewRecordCreated: TypeAlias = bool

@dataclass(frozen=True)
class ListingReference:
    external_id: str
    url: str
    
@dataclass(frozen=True)
class ListingContent:
    html: str
    html_path: str
    images_path: str

@dataclass(frozen=True)
class Source:
    name: str
    seed_urls: list[str]
    
    discover: Callable[[list[SeedUrl]], list[ListingReference]]
    fetch_listing: Callable[[ListingReference], ListingContent]
    parse: Callable[[ListingContent], SourceSpecificListingDict]
    load: Callable[[SourceSpecificListingDict, IngestionRunId, PayloadHash], NewRecordCreated]
    
    hash_payload: Callable[[SourceSpecificListingDict], str]
    