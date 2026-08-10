from ingatlanmizu.ingest.stages import discover_stage
from ingatlanmizu.ingest.tracking import start_run

from .sources.zenga.extract import SEED_URLS, extract
from .sources.zenga.parse import parse
from .sources.zenga.load import load

def main():
    run_id = start_run(source="zenga", metadata={"seed_urls": SEED_URLS})
    discover_stage(run_id=run_id, source="zenga", metadata={"seed_urls": SEED_URLS})
    # extract()
    # for folder, html in extract():
    #     listing = parse(html)
    #     load(listing, folder)
        
if __name__ == "__main__":
    main()