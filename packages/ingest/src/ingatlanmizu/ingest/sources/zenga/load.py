from ingatlanmizu.core.db import connection
import json

def load(listing: dict[str, str|None]):
    if _exists(listing):
        _update(listing)
    else:
        _insert(listing)
        
def _exists(listing: dict[str, str|None]) -> bool:
    if listing.get("hirdeteskod") is None:
        raise ValueError(f"hirdeteskod is missing: {json.dumps(listing)}")
    
    with connection() as conn:
        row = conn.execute("""
            select 1
            from bronze.zenga_listings 
            where hirdeteskod = %s
            limit 1
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
            listing.get("megnevezes"),
            listing.get("ar"),
            listing.get("negyzetmeter_ar"),
            listing.get("cim"),
            listing.get("alapterulet"),
            listing.get("telek"),
            listing.get("emelet"),
            listing.get("szobak_szama"),
            listing.get("leiras"),
            listing.get("hirdeteskod"),
            listing.get("referenciaszam"),
            listing.get("frissitve"),
            listing.get("allapot"),
            listing.get("futes"),
            listing.get("epites_eve"),
            listing.get("terasz"),
            listing.get("energetikai_besorolas"),
            listing.get("hirdeto_neve"),
            listing.get("ingatlan_iroda_neve"),
            listing.get("tipus"),
            listing.get("szintek_szama"),
            json.dumps(listing),
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
            listing.get("megnevezes"),
            listing.get("ar"),
            listing.get("negyzetmeter_ar"),
            listing.get("cim"),
            listing.get("alapterulet"),
            listing.get("telek"),
            listing.get("emelet"),
            listing.get("szobak_szama"),
            listing.get("leiras"),
            listing.get("hirdeteskod"),
            listing.get("referenciaszam"),
            listing.get("frissitve"),
            listing.get("allapot"),
            listing.get("futes"),
            listing.get("epites_eve"),
            listing.get("terasz"),
            listing.get("energetikai_besorolas"),
            listing.get("hirdeto_neve"),
            listing.get("ingatlan_iroda_neve"),
            listing.get("tipus"),
            listing.get("szintek_szama"),
            json.dumps(listing),
            listing.get("hirdeteskod"),
        ))
        conn.commit()