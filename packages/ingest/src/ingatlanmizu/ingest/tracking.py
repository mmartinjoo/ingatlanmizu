from ingatlanmizu.core.db import connection
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
                status = completed,
                completed_at = now()
            where id = %s
        """, (
            run_id
        ))
        conn.commit()