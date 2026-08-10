from bs4 import BeautifulSoup
from ingatlanmizu.ingest.storage import has_images, read_html, write_html, write_image
import requests
import json

SEED_URLS = [
    "https://www.zenga.hu/szombathely+elado+haz",
]

def extract() -> None:
    page_num = 1
    for url in SEED_URLS:
        resp = requests.get(url + f"?page={page_num}")
        resp.raise_for_status()
        _extract_listings(list_page_html=resp.text)
                
def _extract_listings(list_page_html: str) -> None:
    soup = BeautifulSoup(list_page_html, "lxml")
    
    for link in soup.find_all("a"):
        href = link.get("href")
        if href is None:
            continue
        if href.startswith("/ingatlan/") is False:
            continue
        
        id = href.split("/")[-1]
        print(f"extracting {id}")
        
        html = _download_html(url=f"https://zenga.hu{href}")
        write_html(external_id=id, html=html)
        
        _extract_listing_images(id)
                    
def _extract_listing_images(id: str):
    print(f"etracting images for {id}")
    
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
        
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        
        write_image(external_id=id, image_url=url, data=resp.content)
        
def _download_html(url: str) -> str:
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text