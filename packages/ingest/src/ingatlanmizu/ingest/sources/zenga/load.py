from ingatlanmizu.core.db import connection
from ingatlanmizu.ingest.sources.base import SourceSpecificListingDict, IngestionRunId, PayloadHash, NewRecordCreated, ListingReference
import json
import hashlib

def load(
    listing: SourceSpecificListingDict, 
    ingestion_run_id: IngestionRunId,
    payload_hash: PayloadHash,    
) -> NewRecordCreated:
    if listing.get("hirdeteskod") is None:
        raise ValueError(f"hirdeteskod is missing: {json.dumps(listing)}")
    
    if _has_changed(listing=listing, payload_hash=payload_hash) is False:
        return False
    
    with connection() as conn:
        conn.execute(f"""
            insert into bronze.zenga_listing_versions
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
                ingestion_run_id,
                payload_hash,
                megye
            )         
            values
            (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
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
            payload_hash,
            listing.get("megye"),
        ))
        conn.commit()
        
        return True
    
def record_observation(listing: ListingReference, ingestion_run_id: IngestionRunId):
    with connection() as conn:
        conn.execute("""
            insert into bronze.zenga_observations (listing_code, observed_at, ingestion_run_id) 
            values (%s, NOW(), %s)            
        """, (
            listing.external_id,
            ingestion_run_id
        ))
        conn.commit()
        
def _has_changed(listing: SourceSpecificListingDict, payload_hash: PayloadHash) -> bool:
    with connection() as conn:
        row = conn.execute("""
            select payload_hash
            from bronze.zenga_listing_versions
            where hirdeteskod = %s
            order by created_at desc
            limit 1             
        """, (
            listing["hirdeteskod"],
        )).fetchone()
        
        if row is None:
            return True
        
        return False if row[0] == payload_hash else True
            
def hash_payload(listing: SourceSpecificListingDict) -> str:
    payload = {}
    for key, value in listing.items():
        if key in ["html_path", "images_path", "frissitve"]:
            continue
        payload[key] = value
    js = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(js.encode("utf-8")).hexdigest()