from ingatlanmizu.core.db import connection
import json

def load(listing: dict[str, str|None]):
    if _exists(listing):
        _update(listing)
    else:
        _insert(listing)
        
def _exists(listing: dict[str, str|None]) -> bool:
    with connection() as conn:
        row = conn.execute("""
            select * 
            from bronze.zenga_listings 
            where hirdeteskod = %s
        """, 
        (
            listing["hirdeteskod"],
        )).fetchone()
        return row is not None
    
def _insert(listing: dict[str, str|None]) -> None:
    with connection() as conn:
        conn.execute(f"""
            insert into bronze.zenga_listings
            (
                megnevezes,
                ar,
                negyzetmeter_ar,
                cim,
                alapterulet,
                telek,
                emelet,
                szobak_szama,
                leiras,
                hirdeteskod,
                referenciaszam,
                frissitve,
                allapot,
                futes,
                epites_eve,
                terasz,
                energetikai_besorolas,
                hirdeto_neve,
                ingatlan_iroda_neve,
                tipus,
                szintek_szama,
                raw_data
            )         
            values
            (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )    
        """,
        (
            listing["megnevezes"],
            listing["ar"],
            listing["negyzetmeter_ar"],
            listing["cim"],
            listing["alapterulet"],
            listing["telek"],
            listing["emelet"],
            listing["szobak_szama"],
            listing["leiras"],
            listing["hirdeteskod"],
            listing["referenciaszam"],
            listing["frissitve"],
            listing["allapot"],
            listing["futes"],
            listing["epites_eve"],
            listing["terasz"],
            listing["energetikai_besorolas"],
            listing["hirdeto_neve"],
            listing["ingatlan_iroda_neve"],
            listing["tipus"],
            listing["szintek_szama"],
            json.dumps(listing)
        ))
        conn.commit()
        
def _update(listing: dict[str, str|None]) -> None:
    with connection() as conn:
        conn.execute(f"""
            update bronze.zenga_listings
            set
                megnevezes=%s,
                ar=%s,
                negyzetmeter_ar=%s,
                cim=%s,
                alapterulet=%s,
                telek=%s,
                emelet=%s,
                szobak_szama=%s,
                leiras=%s,
                hirdeteskod=%s,
                referenciaszam=%s,
                frissitve=%s,
                allapot=%s,
                futes=%s,
                epites_eve=%s,
                terasz=%s,
                energetikai_besorolas=%s,
                hirdeto_neve=%s,
                ingatlan_iroda_neve=%s,
                tipus=%s,
                szintek_szama=%s,
                raw_data=%s
            where hirdeteskod = %s
        """,
        (
            listing["megnevezes"],
            listing["ar"],
            listing["negyzetmeter_ar"],
            listing["cim"],
            listing["alapterulet"],
            listing["telek"],
            listing["emelet"],
            listing["szobak_szama"],
            listing["leiras"],
            listing["hirdeteskod"],
            listing["referenciaszam"],
            listing["frissitve"],
            listing["allapot"],
            listing["futes"],
            listing["epites_eve"],
            listing["terasz"],
            listing["energetikai_besorolas"],
            listing["hirdeto_neve"],
            listing["ingatlan_iroda_neve"],
            listing["tipus"],
            listing["szintek_szama"],
            json.dumps(listing),
            listing["hirdeteskod"]
        ))
        conn.commit()