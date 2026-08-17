from ingatlanmizu.core.db import connection

def load(data: dict[str, float|None]):
    with connection() as conn:
        conn.execute("truncate table bronze.ksh_inflation_values restart identity")
        
        for month_start in data:
            if data[month_start] is None:
                continue
            
            conn.execute("""
                insert into bronze.ksh_inflation_values(month_start, inflation)
                values (%s, %s)             
            """, (
                month_start,
                data[month_start],
            ))
        
        conn.commit()