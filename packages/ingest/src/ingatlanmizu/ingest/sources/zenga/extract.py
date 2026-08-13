import hashlib

from bs4 import BeautifulSoup
from ingatlanmizu.ingest.storage import has_images, read_html, write_html, write_image, html_file_path_for, folder_for_images
from ingatlanmizu.ingest.sources.base import ListingReference, ListingContent, SeedUrl
import requests
import json
import threading

_local = threading.local()

def _session() -> requests.Session:
    session = getattr(_local, "session", None)
    if session is None:
        session = requests.Session()
        _local.session = session
    return session

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
    write_html(source="zenga", external_id=listing_ref.external_id, html=html)
    fetch_listing_images(listing_ref.external_id)
    
    return ListingContent(
        html=html,
        html_path=html_file_path_for(source="zenga", external_id=listing_ref.external_id),
        images_path=folder_for_images(source="zenga", external_id=listing_ref.external_id),
    )
                
def fetch_listing_images(id: str) -> None:
    if has_images(source="zenga", external_id=id):
        return
    
    html = read_html(source="zenga", external_id=id)
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
        
        write_image(source="zenga", external_id=id, image_url=url, data=resp.content)
        
def _download_html(url: str) -> str:
    resp = _session().get(url, timeout=30)
    resp.raise_for_status()
    return resp.text
