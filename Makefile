add:
	@if [ -z "$(pkg)" ]; then \
		echo "Usage: make add pkg=<pkg_name>"; \
		exit 1; \
	fi
	uv add --package ingatlanmizu-ingest $(pkg)

runingest:
	uv run ingest