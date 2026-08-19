from ingatlanmizu.core.db import connection

def load(data: dict[str, float|None]):
    with connection() as conn:
        for month_start in data:
            if data[month_start] is None:
                continue
            
            row = conn.execute("""
                select exists (
                    select 1
                    from bronze.ksh_inflation_values
                    where month_start = %s
                    and inflation is not null
                )                
            """, (
                month_start,  
            )).fetchone()
            
            if row[0]:
                continue
            
            conn.execute("""
                insert into bronze.ksh_inflation_values(month_start, inflation)
                values (%s, %s)             
            """, (
                month_start,
                data[month_start],
            ))
        
        conn.commit()