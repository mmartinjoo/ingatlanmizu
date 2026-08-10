from ingatlanmizu.ingest.runner import run_extract_item
from ingatlanmizu.ingest.sources.zenga.parse import parse
from ingatlanmizu.ingest.sources.zenga.load import load
from ingatlanmizu.ingest.sources.zenga.extract import discover
from ingatlanmizu.core.db import connection
from ingatlanmizu.ingest.storage import read_html

def discover_stage(run_id: int, source: str, metadata: dict[str, any]):
    if source == "zenga":
        listings = discover(seed_urls=metadata.get("seed_urls"))
        print("discovered_count", len(listings))
        enqueue_run_items(run_id=run_id, listings=listings)
        
def extract_stage(run_id: int):
    run_items = fetch_run_items_by_status(run_id=run_id, status="pending")
    for run_item in run_items:
        run_extract_item(run_item_id=run_item["id"])
        
def load_stage(run_id: int):
    run_items = fetch_run_items_by_status(run_id=run_id, status="extracted")
    for run_item in run_items:
        html = read_html(external_id=run_item["external_id"])
        listing = parse(html)
        load(listing)
        mark_completed(run_item_id=run_item["id"])

def fetch_run_items_by_status(run_id: int, status: str) -> list[dict[str, any]]:
    with connection() as conn:
        rows = conn.execute("""
            select id, external_id
            from ops.ingestion_run_items
            where ingestion_run_id = %s
            and status = %s
        """, (
            run_id,
            status,
        )).fetchall()
        
        return [{"id": r[0], "external_id": r[1]} for r in rows]
    
def mark_completed(run_item_id: int) -> None:
    with connection() as conn:
        conn.execute("""
            update ops.ingestion_run_items
            set status = %s
            where id = %s        
        """, (
            "completed",
            run_item_id,
        ))
        conn.commit()
        
def enqueue_run_items(run_id: int, listings: list[tuple[str, str]]):
    with connection() as conn:
        for listing in listings:
            conn.execute("""
                update ops.ingestion_runs
                set discovered_count = %s
                where ops.ingestion_runs.id = %s
            """,(
                len(listings),
                run_id,
            ))
            
            conn.execute("""
                insert into ops.ingestion_run_items
                (
                    ingestion_run_id,
                    external_id,
                    url,
                    status
                )
                values
                (
                    %s, %s, %s, %s
                )
            """, (
                run_id,
                listing[0],
                listing[1],
                'pending',
            ))
            
            conn.commit()