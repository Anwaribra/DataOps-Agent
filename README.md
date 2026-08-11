# DataOps Agent

An agentic DataOps platform that monitors batch data pipelines, diagnoses data-quality and pipeline failures, and proposes approved remediation actions.

---

## 1. What is DataOps Agent?

**DataOps Agent** is an end-to-end data platform built to demonstrate self-monitoring, diagnostic capabilities, and human-in-the-loop remediation. Rather than acting as a standard data pipeline, DataOps Agent combines automated data ingestion, transformation, data quality testing, asset orchestration, and an AI diagnostic agent.

---

## 2. The Problem It Solves

Most traditional data orchestration systems (e.g., Airflow, Cron, legacy ETL) only alert engineers that **"Job X failed"**.

They do not answer:
- **What actually failed?** (Specific model, test assertion, or asset check)
- **Why did it fail?** (Data corruption, schema drift, null primary key, broken relationship)
- **Which upstream asset caused it?** (Lineage tracing)
- **What changed in the data batch?**
- **What should be done next to fix it?**

DataOps Agent closes the operational loop by automated error diagnosis and remediation planning.

---

## 3. Why This Project Exists

Many data engineering projects focus purely on generic streaming pipelines, dashboards, or basic chatbots. DataOps Agent exists to demonstrate:

- **Observability & Data Quality**: Catching errors early with dbt tests and Dagster asset checks.
- **Deterministic Reliability**: Grounding diagnoses in normalized health signals and rule-based evidence before delegating to LLM reasoning.
- **Standardized MCP Interface**: Exposing diagnostic tools via Model Context Protocol (MCP) to decouple AI reasoning from infrastructure mechanics.
- **Controlled Operational Safety**: The agent **never** silently mutates infrastructure or data. It proposes explicit remediation plans and requires human approval before execution.

---

## 4. Architecture Overview

```text
                    DATA PLATFORM

Sources (E-Commerce Sample JSON Datasets)
   ↓
dlt Ingestion
   ↓
PostgreSQL Raw Layer (raw_data)
   ↓
dbt Layer (staging → intermediate → marts)
   ↓
Dagster Orchestrator (Assets, Lineage, Asset Checks)
   ↓
Health Signals (Normalized Signal Layer & Evidence Collectors)
   ↓
Diagnosis Engine (Deterministic Rule-Based Diagnosis)
   ↓
==================== MCP SERVER ====================
        │                                   │
   Observability                         Evidence
 (Dagster / dbt / Ingestion)      (Incidents / DB Stats)
        │                                   │
        └─────────────────┬─────────────────┘
                          ↓
                  FUTURE AI AGENT
              (COMING IN NEXT STAGE)
```

---

## 5. Technology Stack

- **Ingestion**: Python 3.11+, `dlt` (data load tool)
- **Database**: PostgreSQL 16
- **Transformation & Data Quality**: `dbt` (dbt-core, dbt-postgres)
- **Orchestration & Lineage**: `Dagster` (dagster-webserver, dagster-dbt)
- **Observability & Diagnosis**: Python, `pydantic`, `click` CLI
- **Tool Protocol**: Model Context Protocol (MCP SDK, stdio transport)
- **Agentic Framework (Upcoming)**: Python, Configurable LLM Providers (OpenAI, Anthropic) via environment variables
- **Infrastructure**: Docker, Docker Compose
- **Testing**: `pytest`

---

## 6. Repository Structure

```
.
├── mcp/                    # Model Context Protocol (MCP) Server
│   ├── __init__.py
│   ├── context.py          # Shared application context & database pool
│   ├── schemas.py          # Pydantic schemas for 16 MCP tools
│   ├── server.py           # FastMCP stdio server implementation
│   └── tools/              # Categorized MCP tools
│       ├── dagster.py      # Dagster lineage & status tools
│       ├── dbt.py          # dbt test results & model status tools
│       ├── incidents.py    # Incident & diagnosis tools
│       ├── database.py     # Safe read-only database inspection tools
│       └── ingestion.py    # dlt ingestion status & metadata tools
├── failure_injection/      # Failure Injection Framework (5 deterministic scenarios)
├── health/                 # Health Signal Layer & Evidence Collectors
├── diagnosis/              # Deterministic Rule-Based Diagnosis Engine
├── cli/                    # DataOps CLI tool (dataops inject, reset, diagnose, mcp start)
├── agent/                  # DataOps Agent LLM reasoning placeholder
├── ingestion/              # Ingestion layer using dlt
├── dbt/                    # dbt project (staging, intermediate, marts & tests)
├── dagster/                # Dagster orchestration framework & asset checks
├── data/sample/            # E-commerce JSON sample datasets
├── docs/                   # Platform & MCP tool documentation
│   ├── architecture.md
│   ├── mcp.md
│   └── incidents/
├── tests/                  # Pytest test suite (unit, server & integration tests)
├── docker-compose.yml      # Containerized Postgres & Dagster setup
├── Dockerfile              # Container definition
├── pyproject.toml          # Project dependencies & build config
├── Makefile                # Useful CLI shortcut commands
└── README.md
```

---

## 7. Model Context Protocol (MCP) Layer

The platform provides a complete **MCP Tool Server** exposing 17 standardized, read-only diagnostic tools over standard I/O (`stdio`):

### Available MCP Tools

| Tool Group | Tools | Access Level |
|---|---|---|
| **Dagster** | `get_failed_assets`, `get_asset_status`, `get_asset_lineage`, `get_recent_runs`, `get_asset_checks` | Read-Only |
| **dbt** | `get_dbt_test_results`, `get_dbt_model_status`, `get_failed_dbt_tests` | Read-Only |
| **Incidents** | `list_incidents`, `get_incident`, `get_incident_evidence`, `get_diagnosis` | Read-Only |
| **Database** | `get_table_stats`, `get_column_stats`, `get_recent_data_quality_stats` | Read-Only (Restricted) |
| **Ingestion** | `get_ingestion_status`, `get_ingestion_metadata` | Read-Only |

Start the MCP Server locally:
```bash
dataops mcp start
# Or:
python -m mcp.server
```

---

## 8. How to Run Locally

### Step 1: Environment Setup
```bash
cp .env.example .env
```

### Step 2: Start PostgreSQL Container
```bash
make up
```

### Step 3: Run Ingestion & Transformations
```bash
python -m ingestion.pipeline
make dbt-run
make dbt-test
```

### Step 4: Test Failure Injection, Diagnosis & MCP
```bash
# Inject failure scenario
dataops inject --scenario null_customer_id

# Re-run ingestion & dbt test
python -m ingestion.pipeline
make dbt-test

# Diagnose failure via CLI
dataops diagnose

# Start MCP Server
dataops mcp start

# Reset to healthy pipeline
dataops reset
```

### Step 5: Run Pytest Suite
```bash
make test
# Or: .venv/bin/pytest tests/ -v
```
