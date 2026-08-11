.PHONY: help up down ingest dbt-run dbt-test dagster test build clean inject reset diagnose mcp

help:
	@echo "Available commands:"
	@echo "  make up         - Start Docker Compose services (Postgres, Dagster)"
	@echo "  make down       - Stop Docker Compose services"
	@echo "  make ingest     - Run dlt ingestion pipeline"
	@echo "  make dbt-run    - Run dbt transformations"
	@echo "  make dbt-test   - Run dbt data quality tests"
	@echo "  make dagster    - Launch Dagster webserver locally"
	@echo "  make test       - Run pytest test suite"
	@echo "  make inject     - Inject failure scenario (e.g. make inject SCENARIO=null_customer_id)"
	@echo "  make reset      - Reset failure scenarios to HEALTHY state"
	@echo "  make diagnose   - Run DataOps diagnosis engine"
	@echo "  make mcp        - Start DataOps MCP Server"
	@echo "  make build      - Build Docker containers"
	@echo "  make clean      - Clean cache and temporary build files"

up:
	docker compose up -d

down:
	docker compose down -v

ingest:
	python3 -m ingestion.pipeline

dbt-run:
	cd dbt && dbt run --profiles-dir .

dbt-test:
	cd dbt && dbt test --profiles-dir .

dagster:
	dagster dev -f dagster/definitions.py

test:
	pytest tests/ -v

inject:
	python3 -m failure_injection.runner --scenario $(SCENARIO)

reset:
	python3 -m failure_injection.runner --reset

diagnose:
	python3 -m cli.main diagnose

mcp:
	python3 -m mcp.server

build:
	docker compose build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf dbt/target dbt/dbt_packages
