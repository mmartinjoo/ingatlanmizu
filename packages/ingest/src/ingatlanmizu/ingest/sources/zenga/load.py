from ingatlanmizu.core.db import connection
from ingatlanmizu.ingest.sources.base import SourceSpecificListingDict, IngestionRunId
import json

def load(listing: SourceSpecificListingDict, ingestion_run_id: IngestionRunId):
    if listing.get("hirdeteskod") is None:
        raise ValueError(f"hirdeteskod is missing: {json.dumps(listing)}")
    
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
                raw_data,
                html_path,
                images_path,
                ingestion_run_id
            )         
            values
            (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
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
            listing.get("html_path"),
            listing.get("images_path"),
            ingestion_run_id,
        ))
        conn.commit()