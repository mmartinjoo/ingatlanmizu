from pathlib import Path
from typing import Iterator
from bs4 import BeautifulSoup
import requests
import json
from ingatlanmizu.core.file_utils import read_dir_files

SEED_URLS = [
    "https://www.zenga.hu/szombathely+elado+haz",
    "https://www.zenga.hu/ikervar+elado+haz",
]

def extract() -> Iterator[tuple[str, str]]:
    page_num = 1
    for url in SEED_URLS:
        resp = requests.get(url + f"?page={page_num}")
        resp.raise_for_status()
        
        for folder, html in _extract_listings(list_page_html=resp.text):
            yield folder, html
                
def _extract_listings(list_page_html: str) -> Iterator[tuple[str, str]]:
    soup = BeautifulSoup(list_page_html, "lxml")
    
    for link in soup.find_all("a"):
        href = link.get("href")
        if href is None:
            continue
        if href.startswith("/ingatlan/") is False:
            continue
        
        id = href.split("/")[-1]
        print(f"extracting {id}")
        
        folder = f"/tmp/ingatlanmizu/listings/{id}"
        
        Path(folder).mkdir(parents=True, exist_ok=True)

        html = _download_html(
            url=f"https://zenga.hu{href}",
            filename=f"{folder}/{id}.html"
        )
        
        _extract_listing_images(
            id=id,
            html_path=f"{folder}/{id}.html",
            output_directory=folder,
        )
        
        yield (folder, html)
                    
def _extract_listing_images(id: str, html_path: str, output_directory: str):
    print(f"etracting images for {id}")
    output_path = Path(output_directory)
    
    files = read_dir_files(output_directory)
    images = [f for f in files if f.name.endswith(".webp")]
    
    # images have already been downloaded
    if len(images) > 0:
        return
    
    with open(html_path, "r") as f:
        html = f.read()
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
            
            filename = output_path / Path(url).name
            filename.write_bytes(resp.content)
        
def _download_html(url: str, filename: str) -> str:
    resp = requests.get(url)
    resp.raise_for_status()
    html = resp.text
    with open(filename, "w") as f:
        f.write(html)
        
    return html