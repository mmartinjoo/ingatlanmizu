from pathlib import Path
from typing import Iterator

def read_dir_files(directory: str) -> Iterator[Path]:
    path = Path(directory)
    for file_path in path.iterdir():
        if file_path.is_file():
            yield file_path
            
def read_dir_folders(directory: str) -> Iterator[Path]:
    path = Path(directory)
    for file_path in path.iterdir():
        if file_path.is_dir():
            yield file_path