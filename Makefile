.PHONY: help up down ingest dbt-run dbt-test dagster test build clean inject reset diagnose mcp agent-investigate agent-tools agent-health remediation-list remediation-approve remediation-execute remediation-verify

help:
	@echo "Available commands:"
	@echo "  make up                  - Start Docker Compose services (Postgres, Dagster)"
	@echo "  make down                - Stop Docker Compose services"
	@echo "  make ingest              - Run dlt ingestion pipeline"
	@echo "  make dbt-run             - Run dbt transformations"
	@echo "  make dbt-test            - Run dbt data quality tests"
	@echo "  make dagster             - Launch Dagster webserver locally"
	@echo "  make test                - Run pytest test suite"
	@echo "  make inject              - Inject failure scenario (e.g. make inject SCENARIO=null_customer_id)"
	@echo "  make reset               - Reset failure scenarios to HEALTHY state"
	@echo "  make diagnose            - Run DataOps diagnosis engine"
	@echo "  make mcp                 - Start DataOps MCP Server"
	@echo "  make agent-investigate   - Run AI DataOps Agent investigation (INCIDENT=inc_b91673ef)"
	@echo "  make agent-tools         - Discovered MCP tools via AI Agent"
	@echo "  make agent-health        - Run AI DataOps Agent health check"
	@echo "  make remediation-list    - List active remediation plans"
	@echo "  make remediation-approve - Approve remediation plan (PLAN=plan_id)"
	@echo "  make remediation-execute - Execute approved remediation plan (PLAN=plan_id)"
	@echo "  make remediation-verify  - Verify pipeline recovery (PLAN=plan_id)"
	@echo "  make build               - Build Docker containers"
	@echo "  make clean               - Clean cache and temporary build files"

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

agent-investigate:
	python3 -m agent.cli investigate $(or $(INCIDENT),inc_b91673ef)

agent-tools:
	python3 -m agent.cli tools

agent-health:
	python3 -m agent.cli health

remediation-list:
	python3 -m agent.cli remediation list

remediation-approve:
	python3 -m agent.cli remediation approve $(PLAN)

remediation-execute:
	python3 -m agent.cli remediation execute $(PLAN)

remediation-verify:
	python3 -m agent.cli remediation verify $(PLAN)

build:
	docker compose build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf dbt/target dbt/dbt_packages
