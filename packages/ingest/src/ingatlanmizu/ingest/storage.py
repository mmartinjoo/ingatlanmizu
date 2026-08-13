from pathlib import Path
from typing import Iterator
            
def write_html(source: str, external_id: str, html: str, run_id: int) -> None:
    parent, _, full_path = html_file_path_for(source, external_id, run_id=run_id)
    Path(parent).mkdir(parents=True, exist_ok=True)
    with open(full_path, "w") as f:
        f.write(html)
        
def read_html(source: str, external_id: str, run_id: int) -> str:
    _, _, full_path = html_file_path_for(source, external_id, run_id=run_id)
    with open(full_path, "r") as f:
        return f.read()
        
def has_images(source: str, external_id: str, ext: str = ".webp") -> bool:
    folder = folder_for_images(source, external_id)
    if not Path(folder).exists():
        return False
    
    files = _read_file_paths(folder)
    images = [f for f in files if f.name.endswith(ext)]
    
    return len(images) > 0

def write_image(source: str, external_id: str, image_url: str, data: bytes) -> None:
    folder = folder_for_images(source, external_id)
    Path(folder).mkdir(parents=True, exist_ok=True)
    filename = Path(folder) / Path(image_url).name
    filename.write_bytes(data)
    
def html_file_path_for(source: str, external_id: str, run_id: int) -> tuple[str, str, str]:
    folder = _folder_for(source, external_id, run_id=run_id)
    return folder, f"{external_id}.html", f"{folder}/{external_id}.html"
    
def _folder_for(source: str, external_id: str, run_id: int) -> str:
    path = f"/Users/joomartin/ingatlanmizu/{source}/{run_id}/{external_id}"    
    return path

def folder_for_images(source: str, external_id: str) -> str:
    path = f"/Users/joomartin/ingatlanmizu/{source}/images/{external_id}"
    return path

def _read_file_paths(directory: str) -> Iterator[Path]:
    path = Path(directory)
    for file_path in path.iterdir():
        if file_path.is_file():
            yield file_path