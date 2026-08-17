from os import unlink

import requests
import pandas as pd
from ingatlanmizu.indicators.storage import write_mnb_excel

def fetch() -> pd.DataFrame:
    resp = requests.get("https://www.mnb.hu/root/BaseRate/BaseRateExcel/alapkamat.xlsx")
    resp.raise_for_status()
    
    write_mnb_excel(resp.content)
    
    with open("./alapkamat.xlsx", "wb") as f:
        f.write(resp.content)
        
    df = pd.read_excel("./alapkamat.xlsx")
    
    unlink("./alapkamat.xlsx")
    
    return df