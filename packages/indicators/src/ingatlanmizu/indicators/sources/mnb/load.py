import pandas as pd
from ingatlanmizu.core.db import connection

def load(df: pd.DataFrame) -> None:
    with connection() as conn:
        conn.execute("truncate table bronze.base_rates restart identity")
        
        for _, row in df.iterrows():
            conn.execute("""
                insert into bronze.base_rates(valid_from, valid_until, base_rate)
                values(%s, %s, %s)        
            """, (
                row['valid_from'],        
                row['valid_until'],        
                row['base_rate'],        
            ))
        
        conn.commit()