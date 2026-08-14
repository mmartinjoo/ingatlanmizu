DBT_ENV := set -a && . ./.env && set +a && export DBT_PROFILES_DIR=transform DBT_PROJECT_DIR=transform

add:
	@if [ -z "$(pkg)" ]; then \
		echo "Usage: make add pkg=<pkg_name>"; \
		exit 1; \
	fi
	uv add --package ingatlanmizu-ingest $(pkg)

runingest:
	uv run ingest

runcore:
	uv run core

migrate:
	uv run migrate

dbt-debug:
	@$(DBT_ENV) && uv run dbt debug

dbt-run:
	@$(DBT_ENV) && uv run dbt run

dbt-test:
	@$(DBT_ENV) && uv run dbt test

dbt-build:
	@$(DBT_ENV) && uv run dbt build

dbt-deps: 
	@$(DBT_ENV) && uv run dbt deps

dbt-docs:
	@$(DBT_ENV) && uv run dbt docs generate
	@$(DBT_ENV) && uv run dbt docs serve

deploy:
	./deploy.sh