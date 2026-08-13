from dataclasses import dataclass
import dataclasses
from re import S
from typing import Callable, TypeAlias

SourceSpecificListingDict: TypeAlias = dict[str, str|None]
IngestionRunId: TypeAlias = int
PayloadHash: TypeAlias = str
NewRecordCreated: TypeAlias = bool

@dataclass(frozen=True)
class SeedUrl:
    county: str
    main_type: str
    url: str
    
    def to_dict(self):
        return dataclasses.asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return SeedUrl(
            county=data["county"],
            main_type=data["main_type"],
            url=data["url"],
        )
        
    @classmethod
    def from_dict_many(cls, items: list[dict]) -> list:
        objects = []
        for item in items:
            objects.append(SeedUrl(
                county=item["county"],
                main_type=item["main_type"],
                url=item["url"]
            ))
        return objects

@dataclass(frozen=True)
class ListingReference:
    external_id: str
    url: str
    county: str
    
@dataclass(frozen=True)
class ListingContent:
    html: str
    html_path: str
    images_path: str
    county: str

@dataclass(frozen=True)
class Source:
    name: str
    seed_urls: list[SeedUrl]
    
    discover: Callable[[list[SeedUrl]], list[ListingReference]]
    fetch_listing: Callable[[ListingReference], ListingContent]
    parse: Callable[[ListingContent], SourceSpecificListingDict]
    load: Callable[[SourceSpecificListingDict, IngestionRunId, PayloadHash], NewRecordCreated]
    
    hash_payload: Callable[[SourceSpecificListingDict], str]
    record_observation: Callable[[ListingReference, IngestionRunId], None]