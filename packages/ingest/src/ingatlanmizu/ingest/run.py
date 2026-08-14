from ingatlanmizu.ingest.stages import discover_stage, extract_stage, load_stage
from ingatlanmizu.ingest.tracking import start_run, finish_run
from ingatlanmizu.ingest.sources import get_source
from ingatlanmizu.ingest.sources.zenga import _random_urls

def main():
    source = get_source("zenga")
    run_id = start_run(source=source.name, metadata={"seed_urls": [s.to_dict() for s in source.seed_urls]})
    discover_stage(run_id=run_id)
    extract_stage(run_id=run_id)
    load_stage(run_id=run_id)
    finish_run(run_id=run_id)
        
if __name__ == "__main__":
    main()