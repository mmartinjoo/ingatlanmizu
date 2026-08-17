from ingatlanmizu.core.db import connection

def load(loans: list[dict[str, any]]):
    with connection() as conn:
        for loan in loans:
            conn.execute("""
                delete from bronze.bankmonitor_loans
                where name = %s
                and bank_name = %s
                and available_at = %s             
            """, (
                loan["name"],  
                loan["bank_name"],  
                loan["available_at"],    
            ))
            
            conn.execute("""
                insert into bronze.bankmonitor_loans(
                    name, 
                    bank_name, 
                    available_at, 
                    apr, 
                    monthly_installment, 
                    full_payable_amount
                )
                values (%s, %s, %s, %s, %s, %s)             
            """, (
                loan["name"],  
                loan["bank_name"],  
                loan["available_at"],  
                loan["apr"],  
                loan["monthly_installment"],  
                loan["full_payable_amount"],  
            ))
            conn.commit()