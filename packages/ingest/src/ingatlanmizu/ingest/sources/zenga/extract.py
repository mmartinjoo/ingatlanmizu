import hashlib

from bs4 import BeautifulSoup
from ingatlanmizu.ingest.storage import has_images, read_html, write_html, write_image
from ingatlanmizu.ingest.sources.base import ListingReference, ListingContent, SeedUrl
import requests
import json
import threading

SEED_URLS = [
    "https://www.zenga.hu/szombathely+elado+haz",
]

_local = threading.local()

def _session() -> requests.Session:
    session = getattr(_local, "session", None)
    if session is None:
        session = requests.Session()
        _local.session = session
    return session

def extract() -> None:
    urls = []
    for page_num in range(1,2):
        for url in SEED_URLS:
            urls.append(f"{url}?page={page_num}")
            
    listings = discover(urls)
    for listing in listings:
        fetch_listing(listing=listing)
        
def discover(seed_urls: list[SeedUrl]) -> list[ListingReference]:
    results = []
    for url in seed_urls:
        resp = _session().get(url, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "lxml")
        for link in soup.find_all("a"):
            listing_href = link.get("href")
            if listing_href is None:
                continue
            if listing_href.startswith("/ingatlan/") is False:
                continue
            
            external_id = listing_href.split("/")[-1]
            results.append(ListingReference(
                external_id=external_id,
                url=f"https://zenga.hu{listing_href}",
            ))
            
    return results

def fetch_listing(listing_ref: ListingReference) -> ListingContent:
    print(f"fetching {listing_ref.external_id} at {listing_ref.url}")
    html = _download_html(listing_ref.url)
    write_html(external_id=listing_ref.external_id, html=html)
    fetch_listing_images(listing_ref.external_id)
    
    return ListingContent(
        html=html,
        content_hash=_content_hash(html),
    )
                
def fetch_listing_images(id: str) -> None:
    if has_images(external_id=id):
        return
    
    html = read_html(external_id=id)
    soup = BeautifulSoup(html, "lxml")
    
    urls = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string)
        except (json.JSONDecodeError, TypeError):
            continue

        # @graph is a list of nodes; a page may also have a bare object or list
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data

        for node in nodes:
            img = node.get("image")
            if isinstance(img, str):
                urls.append(img)
            elif isinstance(img, list):
                urls.extend(i for i in img if isinstance(i, str))

    urls_dedup = list(dict.fromkeys(urls))  # dedupe, keep order
    
    for url in urls_dedup:
        if url.startswith("https://images.zenga.hu") is False:
            continue
        if id not in url:
            continue
        
        resp = _session().get(url, timeout=30)
        resp.raise_for_status()
        
        write_image(external_id=id, image_url=url, data=resp.content)
        
def _download_html(url: str) -> str:
    resp = _session().get(url, timeout=30)
    resp.raise_for_status()
    return resp.text

def _content_hash(html: str) -> str:
    return hashlib.sha256(html.encode("utf-8")).hexdigest()