import requests
from datetime import datetime
from ingatlanmizu.indicators.storage import write_ksh_html

def fetch() -> str:
    resp = requests.get("https://www.ksh.hu/stadat_files/ara/hu/ara0040.html")
    resp.raise_for_status()
    
    write_ksh_html(html=resp.text, now=datetime.now())
    
    return resp.text