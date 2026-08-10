from ingatlanmizu.core.db import connection
from ingatlanmizu.ingest.sources.zenga.extract import fetch_listing

def run_extract_item(run_item_id: int):
    try:
        run_item = fetch_run_item(run_item_id=run_item_id)
        mark_extracting(run_item_id=run_item_id)
        
        content_hash = fetch_listing(
            external_id=run_item["external_id"],
            url=run_item["url"],
        )
        
        mark_extracted(
            run_item_id=run_item_id,
            content_hash=content_hash,
        )
    except Exception as exc:
        mark_failed(run_item_id=run_item_id, error_message=str(exc))
        raise exc

def mark_extracting(run_item_id: int) -> None:
    with connection() as conn:
        conn.execute("""
            update ops.ingestion_run_items
            set status = %s
            where id = %s        
        """, (
            "extracting",
            run_item_id,
        ))
        conn.commit()
        
def mark_extracted(run_item_id: int, content_hash: str) -> None:
    with connection() as conn:
        conn.execute("""
            update ops.ingestion_run_items
            set 
                status = %s,
                content_hash = %s
            where id = %s        
        """, (
            "extracted",
            content_hash,
            run_item_id,
        ))
        conn.commit()
        

        
def mark_failed(run_item_id: int, error_message: str) -> None:
    with connection() as conn:
        conn.execute("""
            update ops.ingestion_run_items
            set 
                status = %s,
                error_message = %s
            where id = %s        
        """, (
            "failed",
            error_message,
            run_item_id,
        ))
        conn.commit()
        
def fetch_run_item(run_item_id: int) -> dict[str, any]:
    with connection() as conn:
        row = conn.execute("""
            select external_id, url
            from ops.ingestion_run_items
            where id = %s             
        """, (
            run_item_id,
        )).fetchone()
        
        return {
            "run_item_id": run_item_id,
            "external_id": row[0],
            "url": row[1],
        }