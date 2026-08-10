from ingatlanmizu.ingest.storage import read_html
from ingatlanmizu.ingest.tracking import fetch_run_item, mark_extracting, mark_extracted, mark_failed, mark_completed
from ingatlanmizu.ingest.sources.base import Source

def run_extract_item(source: Source, run_item_id: int):
    try:
        run_item = fetch_run_item(run_item_id=run_item_id)
        mark_extracting(run_item_id=run_item_id)
        
        content_hash = source.fetch_listing(
            run_item["external_id"],
            run_item["url"],
        )
        
        mark_extracted(
            run_item_id=run_item_id,
            content_hash=content_hash,
        )
    except Exception as exc:
        mark_failed(run_item_id=run_item_id, error_message=str(exc))

def run_load_item(source: Source, run_item: dict[str, any]):
    try:
        html = read_html(external_id=run_item["external_id"])
        listing = source.parse(html)
        source.load(listing)
        mark_completed(run_item_id=run_item["id"])
    except Exception as exc:
        mark_failed(run_item_id=run_item["id"], error_message=str(exc))