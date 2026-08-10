from pathlib import Path
from typing import Iterator

def read_file_paths(directory: str) -> Iterator[Path]:
    path = Path(directory)
    for file_path in path.iterdir():
        if file_path.is_file():
            yield file_path
            
def write_html(external_id: str, html: str) -> None:
    folder = _folder_for(external_id)
    with open(f"{folder}/{external_id}.html", "w") as f:
        f.write(html)
        
def read_html(external_id: str) -> str:
    folder = _folder_for(external_id)
    with open(f"{folder}/{external_id}.html", "r") as f:
        return f.read()
        
def has_images(external_id: str, ext: str = ".webp") -> bool:
    folder = _folder_for(external_id)
    files = read_file_paths(folder)
    images = [f for f in files if f.name.endswith(ext)]
    
    return len(images) > 0

def write_image(external_id: str, image_url: str, data: bytes) -> None:
    folder = _folder_for(external_id)
    filename = Path(folder) / Path(image_url).name
    filename.write_bytes(data)
    
def _folder_for(external_id: str) -> str:
    path = f"/tmp/ingatlanmizu/listings/{external_id}"
    Path(path).mkdir(parents=True, exist_ok=True)
    return path