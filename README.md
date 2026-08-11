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

DataOps Agent closes the operational loop by automated error diagnosis, human-approved remediation planning, and recovery verification.

---

## 3. Why This Project Exists

Many data engineering projects focus purely on generic streaming pipelines, dashboards, or basic chatbots. DataOps Agent exists to demonstrate:

- **Observability & Data Quality**: Catching errors early with dbt tests and Dagster asset checks.
- **Deterministic Reliability**: Grounding diagnoses in normalized health signals and rule-based evidence before delegating to LLM reasoning.
- **Standardized MCP Interface**: Exposing diagnostic tools via Model Context Protocol (MCP) to decouple AI reasoning from infrastructure mechanics.
- **Controlled Operational Safety**: The agent **never** silently mutates infrastructure or data. It proposes explicit remediation plans and requires human approval before execution.

---

## 4. End-to-End Closed-Loop Architecture

```text
┌─────────────────────────────────────────────────────┐
│                  DATA SOURCES                       │
└───────────────────────┬─────────────────────────────┘
                        ↓
                       dlt Ingestion
                        ↓
                   PostgreSQL Raw Layer (raw_data)
                        ↓
                       dbt Layer (staging → intermediate → marts)
                        ↓
                    Dagster Orchestrator (Assets & Checks)
                        ↓
              Health Signals & Evidence Collectors
                        ↓
                    Incident System
                        ↓
                 MCP Server (22 Read-Only & Proposal Tools)
                        ↓
                MCP Client (Tool Calling & Discovery)
                        ↓
              LLM DataOps Agent (Diagnosis & Planning)
                        ↓
               Action Validator (Allowlist & Safety Checks)
                        ↓
                HUMAN APPROVAL GATE
                        ↓
               Remediation Engine (Allowlisted Execution)
                        ↓
              Recovery Verification (dbt & Dagster Checks)
                        ↓
                INCIDENT RESOLVED
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
- **Remediation Engine**: Allowlisted actions (`rerun_dagster_asset`, `quarantine_invalid_records`, `refresh_dbt_model`), human approval gate, TTL expiration, audit logger, and recovery verifier.
- **Infrastructure**: Docker, Docker Compose
- **Testing**: `pytest` (58 unit, integration, and safety tests)

---

## 6. Repository Structure

```
.
├── remediation/            # Human-Approved Remediation & Recovery Verification Engine
│   ├── __init__.py
│   ├── actions.py          # Allowlisted actions (rerun_asset, quarantine_records, refresh_dbt)
│   ├── approval.py         # ApprovalService (TTL expiration & self-approval prevention)
│   ├── audit.py            # Immutable AuditLogger & AuditEvent recorder
│   ├── executor.py         # RemediationExecutor with dry-run support
│   ├── models.py           # RemediationPlan & RemediationAction Pydantic models
│   ├── planner.py          # RemediationPlanner converting diagnosis into plans
│   ├── validator.py        # RemediationValidator enforcing safety rules
│   └── verifier.py         # RecoveryVerifier evaluating pipeline recovery
├── agent/                  # AI DataOps Agent (Investigation & Reasoning)
├── mcp/                    # Model Context Protocol (MCP) Server (22 Tools)
├── failure_injection/      # Failure Injection Framework (5 deterministic scenarios)
├── health/                 # Health Signal Layer & Evidence Collectors
├── diagnosis/              # Deterministic Rule-Based Diagnosis Engine
├── cli/                    # DataOps CLI tool
├── ingestion/              # Ingestion layer using dlt
├── dbt/                    # dbt project (staging, intermediate, marts & tests)
├── dagster/                # Dagster orchestration framework & asset checks
├── data/sample/            # E-commerce JSON sample datasets
├── docs/                   # Platform, MCP tool & audit documentation
├── tests/                  # Pytest test suite (58 unit, integration & safety tests)
├── docker-compose.yml      # Containerized Postgres & Dagster setup
├── Dockerfile              # Container definition
├── pyproject.toml          # Project dependencies & build config
├── Makefile                # Useful CLI shortcut commands
└── README.md
```

---

## 7. Model Context Protocol (MCP) Layer

The platform provides a complete **MCP Tool Server** exposing 22 standardized tools over standard I/O (`stdio`):

| Category | Tools | Access Level |
|---|---|---|
| **Dagster** | `get_failed_assets`, `get_asset_status`, `get_asset_lineage`, `get_recent_runs`, `get_asset_checks` | Read-Only |
| **dbt** | `get_dbt_test_results`, `get_dbt_model_status`, `get_failed_dbt_tests` | Read-Only |
| **Incidents** | `list_incidents`, `get_incident`, `get_incident_evidence`, `get_diagnosis` | Read-Only |
| **Database** | `get_table_stats`, `get_column_stats`, `get_recent_data_quality_stats` | Read-Only (Restricted) |
| **Ingestion** | `get_ingestion_status`, `get_ingestion_metadata` | Read-Only |
| **Remediation Proposals** | `propose_remediation`, `validate_remediation`, `get_remediation_plan`, `get_remediation_status`, `get_verification_result` | Read-Only / Proposal |

Start the MCP Server locally:
```bash
dataops mcp start
# Or:
python -m mcp.server
```

---

## 8. Human-Approved Remediation & Recovery Verification

### Why Autonomous Remediation is Dangerous
Unrestricted AI agents with write access to production data platforms risk executing destructive SQL, dropping active tables, or launching runaway backfills.

### Safety Boundaries Enforced
1. **Zero Direct Write Access**: The AI Agent cannot execute arbitrary SQL (`execute_sql`), shell commands, or unapproved scripts.
2. **Allowlisted Actions ONLY**: Execution is restricted strictly to explicit actions:
   - `rerun_dagster_asset`
   - `quarantine_invalid_records` (Idempotent quarantine table insertion without deleting source records)
   - `refresh_dbt_model`
3. **Human Approval Gate**: The AI Agent CANNOT approve its own plan. Human operator approval is mandatory via CLI or API.
4. **Approval TTL Expiration**: Approvals expire after 30 minutes (`REMEDIATION_APPROVAL_TTL_MINUTES=30`). Expired approvals cannot execute.
5. **Recovery Verification Gate**: Incidents only transition to `RESOLVED` after automated recovery verification checks (`Verifier`) confirm dbt test assertions pass and asset failures drop to 0.

---

## 9. How to Run the End-to-End Closed-Loop Workflow

### Step 1: Environment Setup & Postgres
```bash
cp .env.example .env
make up
```

### Step 2: Run Ingestion & Transformations
```bash
python -m ingestion.pipeline
make dbt-run
make dbt-test
```

### Step 3: Inject Data Quality Failure
```bash
dataops inject --scenario null_customer_id
```

### Step 4: Run AI Agent Investigation & Remediation Proposal
```bash
dataops agent investigate inc_b91673ef
# Note the generated Remediation Plan ID (e.g. plan_292b1398)
```

### Step 5: Inspect, Approve, Execute & Verify Recovery
```bash
# 1. Inspect proposed plan
dataops-agent remediation inspect plan_292b1398

# 2. Human Operator Approves Plan
dataops-agent remediation approve plan_292b1398 --approver OPERATOR_JANE

# 3. Execute Controlled Remediation Action
dataops-agent remediation execute plan_292b1398

# 4. Verify Recovery & Resolve Incident
dataops-agent remediation verify plan_292b1398

# 5. Reset pipeline state to healthy
dataops reset
```

### Step 6: Run Pytest Suite
```bash
make test
# Or: .venv/bin/pytest tests/ -v
```
