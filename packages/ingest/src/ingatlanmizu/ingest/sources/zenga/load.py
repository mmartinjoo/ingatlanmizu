from ingatlanmizu.core.db import connection
import json

def load(listing: dict[str, str|None]):
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