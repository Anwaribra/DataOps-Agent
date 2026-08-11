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
MCP SERVER (17 Read-Only MCP Tools)
   ↓
MCP CLIENT (Tool Discovery & Execution)
   ↓
LLM DATAOPS AGENT (Evidence-Based Investigation & Recommendation)
```

---

## 5. Technology Stack

- **Ingestion**: Python 3.11+, `dlt` (data load tool)
- **Database**: PostgreSQL 16
- **Transformation & Data Quality**: `dbt` (dbt-core, dbt-postgres)
- **Orchestration & Lineage**: `Dagster` (dagster-webserver, dagster-dbt)
- **Observability & Diagnosis**: Python, `pydantic`, `click` CLI
- **Tool Protocol**: Model Context Protocol (MCP SDK, stdio transport)
- **Agentic Framework**: Python, Configurable LLM Providers (`LLMProvider` abstraction with `FakeLLMProvider` for deterministic testing and `OpenAILLMProvider` for live model execution)
- **Infrastructure**: Docker, Docker Compose
- **Testing**: `pytest`

---

## 6. Repository Structure

```
.
├── agent/                  # AI DataOps Agent
│   ├── __init__.py
│   ├── agent.py            # Core investigation loop & budget management
│   ├── client.py           # DataOpsMCPClient connecting to MCP tools
│   ├── cli.py              # dataops-agent CLI commands (investigate, tools, health)
│   ├── models.py           # AgentState & AgentDiagnosis Pydantic models
│   ├── prompts.py          # SYSTEM_DATAOPS_AGENT_PROMPT & safety rules
│   ├── provider.py         # LLMProvider abstraction & FakeLLMProvider
│   └── tracing.py          # InvestigationTrace step recorder
├── mcp/                    # Model Context Protocol (MCP) Server
│   ├── context.py          # Shared application context & database pool
│   ├── schemas.py          # Pydantic schemas for 17 MCP tools
│   ├── server.py           # FastMCP stdio server implementation
│   └── tools/              # Categorized MCP tools (Dagster, dbt, Incidents, Database, Ingestion)
├── failure_injection/      # Failure Injection Framework (5 deterministic scenarios)
├── health/                 # Health Signal Layer & Evidence Collectors
├── diagnosis/              # Deterministic Rule-Based Diagnosis Engine
├── cli/                    # DataOps CLI tool
├── ingestion/              # Ingestion layer using dlt
├── dbt/                    # dbt project (staging, intermediate, marts & tests)
├── dagster/                # Dagster orchestration framework & asset checks
├── data/sample/            # E-commerce JSON sample datasets
├── docs/                   # Platform & MCP tool documentation
├── tests/                  # Pytest test suite (49 unit, integration & safety tests)
├── docker-compose.yml      # Containerized Postgres & Dagster setup
├── Dockerfile              # Container definition
├── pyproject.toml          # Project dependencies & build config
├── Makefile                # Useful CLI shortcut commands
└── README.md
```

---

## 7. AI DataOps Agent

The **AI DataOps Agent** operates as an autonomous operational data engineer investigating pipeline incidents through MCP tools.

### Why the Agent Uses MCP
The agent communicates strictly through the MCP Client layer. Direct infrastructure access (raw SQL queries, shell commands, file modifications, or direct Dagster/dbt mutations) is disabled by design. This guarantees strict read-only governance and decoupled architecture.

### Investigation Lifecycle
1. **Receive Incident**: Initiates investigation loop with incident ID.
2. **Tool Discovery**: MCP client dynamically connects to MCP server and retrieves available tool definitions.
3. **Evidence-Based Investigation**: The agent reasons over missing evidence, selecting appropriate tools (e.g. `get_failed_assets`, `get_failed_dbt_tests`, `get_asset_lineage`, `get_column_stats`).
4. **Facts vs Inferences**: Observed tool results are classified as facts, separate from model inferences and hypothesis statements.
5. **Confidence Calculation**: Evidence agreement computes confidence levels (`HIGH`, `MEDIUM`, `LOW`).
6. **Structured Diagnosis**: Produces an auditable report detailing root cause, impact, observed facts, and recommended actions.
7. **Safety Boundary (Execution Halt)**: The agent halts before executing any remediation, requiring explicit human operator approval.

---

## 8. Development Roadmap

### Phase 4 — Implemented
- [x] Configurable `LLMProvider` abstraction (`FakeLLMProvider` & `OpenAILLMProvider`)
- [x] MCP Client integration & tool discovery
- [x] Tool-calling investigation loop
- [x] Step and tool-call budget limits (`MAX_TOOL_CALLS=15`, `MAX_INVESTIGATION_STEPS=10`)
- [x] Evidence-based root-cause diagnosis & impact analysis
- [x] Investigation step tracing (`InvestigationTrace`)
- [x] Safety boundaries (Read-only enforcement, write execution blocked)

### Phase 5 — Planned
- [ ] Human-in-the-loop approval workflow
- [ ] Controlled remediation execution (quarantines, dbt model reruns, source batch backfills)
- [ ] Post-remediation recovery verification

---

## 9. How to Run Locally

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

### Step 4: Inject Failure & Run AI DataOps Agent
```bash
# Inject failure scenario
dataops inject --scenario null_customer_id

# Check agent health & discovered tools
dataops agent health
dataops agent tools

# Run AI Agent investigation
dataops agent investigate inc_b91673ef

# Reset pipeline to healthy
dataops reset
```

### Step 5: Run Pytest Suite
```bash
make test
# Or: .venv/bin/pytest tests/ -v
```
