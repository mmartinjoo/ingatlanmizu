from .sources.zenga.extract import extract
from .sources.zenga.parse import parse
from .sources.zenga.load import load

def main():
    for folder, html in extract():
        listing = parse(html)
        load(listing, folder)
        
if __name__ == "__main__":
    main()