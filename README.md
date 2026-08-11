# DataOps Agent

An agentic DataOps platform that monitors batch data pipelines, diagnoses data-quality failures via Model Context Protocol (MCP) tools, and executes human-approved recovery workflows.

---

## 1. What It Does

DataOps Agent closes the operational loop for data engineering pipelines:

```text
Observe → Investigate → Diagnose → Approve → Remediate → Verify → Resolve
```

1. **Detects**: Catches data quality violations using `dbt` test assertions and Dagster asset checks.
2. **Investigates**: Traces upstream lineage and column metrics via 22 standardized read-only **Model Context Protocol (MCP)** tools.
3. **Diagnoses**: Produces evidence-grounded root cause reports with confidence scores.
4. **Proposes**: Formulates allowlisted remediation plans with risk assessments.
5. **Requires Approval**: Enforces a strict **Human Approval Gate** (the AI Agent is forbidden from approving its own actions).
6. **Remediates**: Executes idempotent allowlisted actions (`quarantine_invalid_records`, `refresh_dbt_model`, `rerun_dagster_asset`).
7. **Verifies**: Audits post-remediation data assertions and asset health before marking incidents **RESOLVED**.

---

## 2. End-to-End System Architecture

```text
                                OpenShip / Docker Compose
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     │                                           │
               Next.js Web UI                              FastAPI Backend
             (web/ : Port 3000)                           (api/ : Port 8000)
                     │                                           │
                     │          ┌────────────────────────────────┼────────────────────────────────┐
                     │          │                                │                                │
                     │   PostgreSQL (5433)                Dagster (3000)                     MCP Server
                     │          │                                │                                │
                     │          └────────────────────────────────┼────────────────────────────────┘
                     │                                           │
                     │                                     DataOps Agent
                     │                                           │
                     │                                    Remediation Engine
                     │                                           │
                     └───────────────────── REST API ────────────┘
```

---

## 3. Technology Stack

- **Ingestion**: Python 3.11+, `dlt` (data load tool)
- **Database**: PostgreSQL 16
- **Transformation & Data Quality**: `dbt` (dbt-core, dbt-postgres) with 27 data quality assertions
- **Orchestration & Lineage**: `Dagster` (dagster-webserver, dagster-dbt)
- **Observability & Diagnosis**: Pydantic health signal layer, deterministic diagnosis engine
- **Tool Protocol**: Model Context Protocol (FastMCP SDK, stdio transport, 22 tools)
- **Agentic Engine**: Python, Configurable `LLMProvider` (`FakeLLMProvider` for deterministic testing & `OpenAILLMProvider` for live OpenAI calls)
- **Remediation Engine**: Allowlisted execution, `ApprovalService` (30m TTL & self-approval block), `RemediationExecutor`, and `RecoveryVerifier`
- **Backend Adapter**: FastAPI (`api/main.py`), Uvicorn
- **Web Control Plane**: Next.js 15, TypeScript, Tailwind CSS, Lucide icons, Dark/Light mode theme engine (`web/`)
- **Testing**: `pytest` (64 unit, integration, API, and safety tests)

---

## 4. Web Control Plane (`web/`)

The repository includes a modern web operational control plane located in `web/`:

- **Live Mode**: Connects directly to the FastAPI backend adapter (`http://localhost:8000/api`) to display live pipeline nodes, incident logs, MCP investigation steps, and execution status.
- **Demo / Sandbox Mode**: Provides a deterministic sandbox simulation for public web deployments where backend credentials are isolated.
- **Design Philosophy**: Built using the rounded design system and dark-first visual language of the **Ayn platform** (`https://aynplatform.app/`).

---

## 5. OpenShip & Multi-Service Deployment

The platform is configured for multi-service deployment on OpenShip or Docker Compose:

| Service | Technology | Port | Description |
|---|---|---|---|
| `postgres` | PostgreSQL 16 | 5433:5432 | Primary relational store (`raw_data`, `staging`, `intermediate`, `marts`) |
| `dagster` | Dagster 1.6+ | 3000:3000 | Software-defined asset orchestrator & lineage UI |
| `api` | FastAPI / Uvicorn | 8000:8000 | REST API adapter exposing system state & remediation endpoints |
| `web` | Next.js 15 | 3001:3000 | Production Next.js operational control center |

Start the full stack with Docker Compose:
```bash
make docker-up
```

Stop the full stack:
```bash
make docker-down
```

---

## 6. How to Run Locally

### Option A: Local Development Mode
```bash
# 1. Start Postgres database container
make up

# 2. Ingest raw data & run dbt transformations
python -m ingestion.pipeline
make dbt-run
make dbt-test

# 3. Start FastAPI backend adapter (Terminal 1)
make api-dev

# 4. Start Next.js web control plane (Terminal 2)
make web-dev
```

### Option B: Pytest Test Suite
```bash
make test
# Or: .venv/bin/pytest tests/ -v
```

---

## 7. Safety Statement

> **AI proposes. Humans approve. The system executes.**

1. **Zero Direct Write Access**: The AI Agent interacts exclusively through read-only and proposal MCP tools. Raw SQL (`execute_sql`) and shell commands are forbidden.
2. **Mandatory Human Approval**: The AI Agent cannot approve its own plan. Approvals require human operator interaction and expire after 30 minutes.
3. **Allowlisted Execution**: Remediation is strictly restricted to explicit allowlisted actions (`quarantine_invalid_records`, `refresh_dbt_model`, `rerun_dagster_asset`).
