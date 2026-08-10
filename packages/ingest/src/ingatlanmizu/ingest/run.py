from ingatlanmizu.ingest.sources.zenga.extract import SEED_URLS
from ingatlanmizu.ingest.stages import discover_stage, extract_stage, load_stage
from ingatlanmizu.ingest.tracking import start_run, finish_run

def main():
    run_id = start_run(source="zenga", metadata={"seed_urls": SEED_URLS})
    discover_stage(run_id=run_id, source="zenga", metadata={"seed_urls": SEED_URLS})
    extract_stage(run_id=run_id)
    load_stage(run_id=run_id)
    finish_run(run_id=run_id)
        
if __name__ == "__main__":
    main()