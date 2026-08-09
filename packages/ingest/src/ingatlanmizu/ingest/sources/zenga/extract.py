from pathlib import Path
from bs4 import BeautifulSoup
import requests
import json
from ingatlanmizu.core.file_utils import read_dir_files

SEED_URLS = [
    "https://www.zenga.hu/szombathely+elado+haz"
]

def extract():
    _extract_seed_urls()
    _extract_listings()

def _extract_seed_urls():
    page_num = 1
    for url in SEED_URLS:
        resp = requests.get(url + f"?page={page_num}")
        resp.raise_for_status()
        _extract_listings(list_page_html=resp.text)
                
def _extract_listings(list_page_html: str):
    soup = BeautifulSoup(list_page_html, "lxml")
    
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and href.startswith("/ingatlan/"):
            id = href.split("/")[-1]
            print(f"extracting {id}")
            Path(f"/tmp/ingatlanmizu/listings/{id}").mkdir(parents=True, exist_ok=True)

            _download_html(
                url=f"https://zenga.hu{href}",
                filename=f"/tmp/ingatlanmizu/listings/{id}/{id}.html"
            )
            
            _extract_listing_images(
                id=id,
                html_path=f"/tmp/ingatlanmizu/listings/{id}/{id}.html",
                output_directory=f"/tmp/ingatlanmizu/listings/{id}",
            )
                    
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
    with open(filename, "w") as f:
        f.write(resp.text)