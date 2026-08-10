from concurrent.futures import ThreadPoolExecutor, as_completed
from ingatlanmizu.core.config import settings
from ingatlanmizu.ingest.runner import run_extract_item, run_load_item
from ingatlanmizu.ingest.tracking import enqueue_run_items, dequeue_run_items, fetch_run
from ingatlanmizu.ingest.sources.base import Source
from ingatlanmizu.ingest.sources import get_source

def discover_stage(run_id: int):
    source, metadata = _source_for(run_id)
    listings = source.discover(metadata.get("seed_urls"))
    enqueue_run_items(run_id=run_id, listings=listings)
        
def extract_stage(run_id: int):
    source, _ = _source_for(run_id)
    run_items = dequeue_run_items(run_id=run_id, status="pending")
    with ThreadPoolExecutor(max_workers=settings.ingest_max_workers) as pool:
        futures = [
            pool.submit(run_extract_item, source, run_item["id"])
            for run_item in run_items
        ]
        
        for future in as_completed(futures):
            future.result()
        
def load_stage(run_id: int):
    source, _ = _source_for(run_id)
    run_items = dequeue_run_items(run_id=run_id, status="extracted")
    for run_item in run_items:
        run_load_item(source, run_item=run_item)
        
def _source_for(run_id: int) -> tuple[Source, dict]:
    run = fetch_run(run_id=run_id)
    return get_source(run["source"]), run["metadata"]