from ingatlanmizu.ingest.storage import read_html, folder_for_images
from ingatlanmizu.ingest.tracking import fetch_run_item, mark_extracting, mark_extracted, mark_failed, mark_completed
from ingatlanmizu.ingest.sources.base import Source, ListingReference, ListingContent
import traceback

def run_extract_item(source: Source, run_item_id: int):
    try:
        run_item = fetch_run_item(run_item_id=run_item_id)
        mark_extracting(run_item_id=run_item_id)
        
        source.fetch_listing(
            ListingReference(
                external_id=run_item["external_id"],
                url=run_item["url"],
                county=run_item["county"],
            ),
            run_id=run_item["ingestion_run_id"]
        )
        
        mark_extracted(
            run_item_id=run_item_id,
        )
    except Exception:
        mark_failed(run_item_id=run_item_id, error_message=traceback.format_exc())

def run_load_item(source: Source, run_item: dict[str, any]):
    try:
        path, html = read_html(
            source=source.name, 
            external_id=run_item["external_id"], 
            run_id=run_item["ingestion_run_id"],
        )
        
        listing_content = ListingContent(
            html=html,
            html_path=path,
            images_path=folder_for_images(source=source.name, external_id=run_item["external_id"]),
            county=run_item["county"],
        )
        listing = source.parse(listing_content)
        payload_hash = source.hash_payload(listing)
        new_record_created = source.load(listing, run_item["ingestion_run_id"], payload_hash)
        mark_completed(run_item_id=run_item["id"], new_record_created=new_record_created)
    except Exception:
        mark_failed(run_item_id=run_item["id"], error_message=traceback.format_exc())