from pathlib import Path
from bs4 import BeautifulSoup
import requests

SEED_URLS = [
    "https://www.zenga.hu/szombathely+elado+haz"
]

def extract():
    _extract_seed_urls()
    _extract_listings()

def _extract_seed_urls():
    for url in SEED_URLS:
        for page_num in range(1, 3):
            _download_html(
                url=url + f"?page={page_num}",
                filename=f"/tmp/ingatlanmizu/zenga_{page_num}.html"
            )
                
def _extract_listings():
    for file_path in _read_dir("/tmp/ingatlanmizu"):
        with open(file_path, "r") as f:
            content = f.read()
            soup = BeautifulSoup(content, "html.parser")
            
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
                        html_path=f"/tmp/ingatlanmizu/listings/{id}/{id}.html",
                        output_directory=f"/tmp/ingatlanmizu/listings/{id}",
                    )
                    
def _extract_listing_images(html_path: str, output_directory: str):
    print(f"etracting images {output_directory}")
    output_path = Path(output_directory)
    with open(html_path, "r") as f:
        html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue
            if src.startswith("https://images.zenga.hu") is False:
                continue
            
            print(f"extracting {src}")
            
            resp = requests.get(src, timeout=30)
            resp.raise_for_status()
            
            filename = output_path / Path(src).name
            filename.write_bytes(resp.content)
                        
def _read_dir(directory):
    directory = Path(directory)
    for file_path in directory.iterdir():
        if file_path.is_file():
            yield file_path
            
def _download_html(url: str, filename: str) -> str:
    resp = requests.get(url)
    with open(filename, "w") as f:
        f.write(resp.text)