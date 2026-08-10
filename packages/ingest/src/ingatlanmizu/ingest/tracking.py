from ingatlanmizu.core.db import connection
from ingatlanmizu.ingest.sources.base import ListingReference
import json

def start_run(source: str, metadata: dict[str, any]) -> int:
    with connection() as conn:
        row = conn.execute("""
            insert into ops.ingestion_runs
            (
                source,
                started_at,
                metadata,
                status
            )            
            values
            (
                %s, NOW(), %s, %s
            ) 
            returning id
        """, (
            source,
            json.dumps(metadata),
            "running",
        )).fetchone()
        conn.commit()
        
        return int(row[0])
    
def finish_run(run_id: int) -> None:
    with connection() as conn:
        conn.execute("""
            update ops.ingestion_runs
            set 
                status = %s,
                completed_at = now()
            where id = %s
        """, (
            "completed",
            run_id,
        ))
        conn.commit()
        
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
        
def mark_extracted(run_item_id: int) -> None:
    with connection() as conn:
        conn.execute("""
            update ops.ingestion_run_items
            set 
                status = %s
            where id = %s        
        """, (
            "extracted",
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
        
def enqueue_run_items(run_id: int, listings: list[ListingReference]):
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
                listing.external_id,
                listing.url,
                'pending',
            ))
            
            conn.commit()
            
def dequeue_run_items(run_id: int, status: str) -> list[dict[str, any]]:
    with connection() as conn:
        rows = conn.execute("""
            select id, external_id, ingestion_run_id
            from ops.ingestion_run_items
            where ingestion_run_id = %s
            and status = %s
        """, (
            run_id,
            status,
        )).fetchall()
        
        return [{"id": r[0], "external_id": r[1], "ingestion_run_id": r[2]} for r in rows]
    
def fetch_run(run_id: int) -> dict[str, any]:
    with connection() as conn:
        row = conn.execute("""
            select id, source, metadata
            from ops.ingestion_runs
            where id = %s 
            limit 1            
        """, (
            run_id,
        )).fetchone();
        
        return {
            "id": row[0],
            "source": row[1],
            "metadata": row[2],
        }