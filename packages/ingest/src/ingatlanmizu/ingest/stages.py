from ingatlanmizu.ingest.runner import run_extract_item, run_load_item
from ingatlanmizu.ingest.sources.zenga.extract import discover
from ingatlanmizu.ingest.tracking import enqueue_run_items, dequeue_run_items

def discover_stage(run_id: int, source: str, metadata: dict[str, any]):
    if source == "zenga":
        listings = discover(seed_urls=metadata.get("seed_urls"))
        enqueue_run_items(run_id=run_id, listings=listings)
        
def extract_stage(run_id: int):
    run_items = dequeue_run_items(run_id=run_id, status="pending")
    for run_item in run_items:
        run_extract_item(run_item_id=run_item["id"])
        
def load_stage(run_id: int):
    run_items = dequeue_run_items(run_id=run_id, status="extracted")
    for run_item in run_items:
        run_load_item(run_item=run_item)