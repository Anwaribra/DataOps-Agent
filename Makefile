PYTHON ?= $(shell test -x .venv/bin/python && echo .venv/bin/python || echo python3)
PYTEST ?= $(shell test -x .venv/bin/pytest && echo .venv/bin/pytest || echo pytest)

.PHONY: help up down ingest dbt-run dbt-test dagster test build clean inject reset diagnose mcp agent-investigate agent-tools agent-health remediation-list remediation-approve remediation-execute remediation-verify api-dev web-dev web-build docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make up                  - Start Postgres Docker container"
	@echo "  make down                - Stop Postgres Docker container"
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
	@echo "  make api-dev             - Run FastAPI backend adapter locally"
	@echo "  make web-dev             - Run Next.js demo web control plane locally"
	@echo "  make web-build           - Build production Next.js demo website"
	@echo "  make docker-up           - Build and start full multi-service stack (Postgres, Dagster, API, Web)"
	@echo "  make docker-down         - Stop full multi-service stack"
	@echo "  make build               - Build Docker containers"
	@echo "  make clean               - Clean cache and temporary build files"

up:
	docker compose up -d postgres

down:
	docker compose down -v

ingest:
	$(PYTHON) -m ingestion.pipeline

dbt-run:
	cd dbt && dbt run --profiles-dir .

dbt-test:
	cd dbt && dbt test --profiles-dir .

dagster:
	dagster dev -f dagster/definitions.py

test:
	$(PYTEST) tests/ -v

inject:
	$(PYTHON) -m failure_injection.runner --scenario $(SCENARIO)

reset:
	$(PYTHON) -m failure_injection.runner --reset

diagnose:
	$(PYTHON) -m cli.main diagnose

mcp:
	$(PYTHON) -m mcp.server

agent-investigate:
	$(PYTHON) -m agent.cli investigate $(or $(INCIDENT),inc_b91673ef)

agent-tools:
	$(PYTHON) -m agent.cli tools

agent-health:
	$(PYTHON) -m agent.cli health

remediation-list:
	$(PYTHON) -m agent.cli remediation list

remediation-approve:
	$(PYTHON) -m agent.cli remediation approve $(PLAN)

remediation-execute:
	$(PYTHON) -m agent.cli remediation execute $(PLAN)

remediation-verify:
	$(PYTHON) -m agent.cli remediation verify $(PLAN)

api-dev:
	uvicorn api.main:app --reload --port 8000

web-dev:
	cd web && npm run dev

web-build:
	cd web && npm run build

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down -v

build:
	docker compose build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf dbt/target dbt/dbt_packages web/.next
