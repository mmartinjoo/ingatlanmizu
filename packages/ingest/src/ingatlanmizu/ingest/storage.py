from pathlib import Path
from typing import Iterator
from datetime import datetime
            
def write_html(source: str, external_id: str, html: str) -> None:
    folder = _folder_for(source, external_id)
    with open(f"{folder}/{external_id}.html", "w") as f:
        f.write(html)
        
def read_html(source: str, external_id: str) -> str:
    folder = _folder_for(source, external_id)
    with open(f"{folder}/{external_id}.html", "r") as f:
        return f.read()
        
def has_images(source: str, external_id: str, ext: str = ".webp") -> bool:
    folder = _folder_for_images(source, external_id)
    files = _read_file_paths(folder)
    images = [f for f in files if f.name.endswith(ext)]
    
    return len(images) > 0

def write_image(source: str, external_id: str, image_url: str, data: bytes) -> None:
    folder = _folder_for_images(source, external_id)
    filename = Path(folder) / Path(image_url).name
    filename.write_bytes(data)
    
def _folder_for(source: str, external_id: str) -> str:
    date = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%H%M")
    path = f"/tmp/ingatlanmizu/{source}/{date}/{timestamp}/{external_id}"
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def _folder_for_images(source: str, external_id: str) -> str:
    path = f"/tmp/ingatlanmizu/{source}/images/{external_id}"
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def _read_file_paths(directory: str) -> Iterator[Path]:
    path = Path(directory)
    for file_path in path.iterdir():
        if file_path.is_file():
            yield file_path