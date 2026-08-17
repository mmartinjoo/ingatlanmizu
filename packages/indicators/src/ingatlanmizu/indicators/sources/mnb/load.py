import requests
from ingatlanmizu.indicators.storage import write_mnb_excel

def load():
    resp = requests.get("https://www.mnb.hu/root/BaseRate/BaseRateExcel/alapkamat.xlsx")
    resp.raise_for_status()
    
    write_mnb_excel(resp.content)