import pandas as pd
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def parse(df: pd.DataFrame) -> pd.DataFrame:
    df_renamed = df.rename(columns={
        "Jegybanki alapkamat mértékéről szóló rendelet hatálybalépésének időpontja": "valid_from",
        "Jegybanki alapkamat mértéke": "base_rate_pct"
    })
    
    for col_name, values in df_renamed.items():
        if col_name != "valid_from":
            continue
        
        for i in range(len(values)-1, -1, -1):
            if i == 0:
                valid_until = datetime.now() + timedelta(days=90)
            else:
                valid_until = values[i-1] - timedelta(days=1)
                
            valid_until = valid_until.strftime("%Y-%m-%d")
            df_renamed.at[i, "valid_until"] = valid_until
            
    for col_name, values in df_renamed.items():
        if col_name != "base_rate_pct":
            continue
        
        for i, value in values.items():
            new_value = re.sub('%', '', value)
            new_value = re.sub(',', '.', new_value)
            df_renamed.at[i, "base_rate"] = float(new_value)
                
    df_renamed['valid_from'] = df_renamed['valid_from'].apply(lambda x: x.strftime("%Y-%m-%d"))
            
    return df_renamed.drop(columns=["base_rate_pct"])
    