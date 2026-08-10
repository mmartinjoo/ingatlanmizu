from ingatlanmizu.ingest.sources.zenga.extract import discover
from ingatlanmizu.core.db import connection

def discover_stage(run_id: int, source: str, metadata: dict[str, any]):
    if source == "zenga":
        listings = discover(seed_urls=metadata.get("seed_urls"))
        enqueue_run_items(run_id=run_id, listings=listings)
        
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