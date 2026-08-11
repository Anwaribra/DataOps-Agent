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
- **Controlled Operational Safety**: The agent **never** silently mutates infrastructure or data. It proposes explicit remediation plans and requires human approval before execution.

---

## 4. Architecture Overview

```
+------------------------+
|  External Data Source  | (E-Commerce Sample JSON Datasets)
+-----------+------------+
            |
            v
+------------------------+
|     dlt Ingestion      | (Extract & Load into PostgreSQL)
+-----------+------------+
            |
            v
+------------------------+
|  PostgreSQL Raw Layer  | (raw_data.customers, orders, etc.)
+-----------+------------+
            |
            v
+------------------------+
|       dbt Layer        | (staging -> intermediate -> marts)
+-----------+------------+
            |
            v
+------------------------+
|   Dagster Orchestrator | (Asset Lineage, Asset Checks, Jobs)
+-----------+------------+
            |
            v
+------------------------+
|     Health Signals     | (Normalized Signal Layer & Evidence Collectors)
+-----------+------------+
            |
            v
+------------------------+
|    Diagnosis Engine    | (Deterministic Rule-Based Diagnosis Engine)
+-----------+------------+
            |
            v
+------------------------+
|  MCP / DataOps Agent   | (Model Context Protocol & LLM Reasoning)
+------------------------+
```

---

## 5. Technology Stack

- **Ingestion**: Python 3.11+, `dlt` (data load tool)
- **Database**: PostgreSQL 16
- **Transformation & Data Quality**: `dbt` (dbt-core, dbt-postgres)
- **Orchestration & Lineage**: `Dagster` (dagster-webserver, dagster-dbt)
- **Observability & Diagnosis**: Python, `pydantic`, `click` CLI
- **Agentic Framework**: Python, Configurable LLM Providers (OpenAI, Anthropic) via environment variables
- **Agent Tooling**: Model Context Protocol (MCP)
- **Infrastructure**: Docker, Docker Compose
- **Testing**: `pytest`

---

## 6. Repository Structure

```
.
├── failure_injection/      # Failure Injection Framework
│   ├── __init__.py
│   ├── scenarios.py        # 5 deterministic failure scenario definitions
│   ├── runner.py           # Failure injection CLI runner
│   └── README.md
├── health/                 # Health Signal Layer & Evidence Collectors
│   ├── __init__.py
│   ├── models.py           # SignalType, Severity, HealthSignal models
│   ├── collectors.py       # Evidence collectors (failed assets, lineage, dbt results)
│   └── aggregator.py       # Signal aggregator
├── diagnosis/              # Deterministic Rule-Based Diagnosis Engine
│   ├── __init__.py
│   ├── models.py           # Incident & IncidentStatus pydantic models
│   ├── rules.py            # Rule definitions mapping signals to root cause & actions
│   └── engine.py           # Diagnosis engine evaluation loop
├── cli/                    # DataOps CLI tool
│   ├── __init__.py
│   └── main.py             # Click CLI commands (dataops inject, reset, diagnose, incident)
├── agent/                  # DataOps Agent LLM reasoning placeholder
├── mcp/                    # Model Context Protocol server placeholder
├── ingestion/              # Ingestion layer using dlt
│   ├── __init__.py
│   └── pipeline.py         # dlt pipeline with failure injection hooks
├── dbt/                    # dbt project (staging, intermediate, marts & tests)
├── dagster/                # Dagster orchestration framework & asset checks
├── data/sample/            # E-commerce JSON sample datasets
├── docs/incidents/         # Detailed incident scenario documentation
├── tests/                  # Pytest test suite (28 deterministic tests)
├── docker-compose.yml      # Containerized Postgres & Dagster setup
├── Dockerfile              # Container definition
├── pyproject.toml          # Project dependencies & build config
├── Makefile                # Useful CLI shortcut commands
└── README.md
```

---

## 7. Incident Detection & Diagnosis

The platform establishes a complete, deterministic incident detection and error diagnosis framework prior to introducing AI reasoning:

### How Failures are Injected
The platform includes a dedicated **Failure Injection Framework** (`failure_injection/`) supporting 5 deterministic, reversible, and isolated scenarios:
- `null_customer_id`: Injects NULL values into order records.
- `duplicate_order_id`: Injects duplicate order_id records.
- `invalid_status`: Injects unsupported status string (`"UNKNOWN_STATUS"`).
- `referential_integrity`: Injects order referencing a non-existent customer (`"cust_non_existent_999"`).
- `volume_anomaly`: Injects abnormal batch volume (500+ order records).

Run failure injection:
```bash
python -m failure_injection.runner --scenario null_customer_id
# Or via DataOps CLI:
dataops inject --scenario null_customer_id
```

Reset back to healthy pipeline state:
```bash
dataops reset
```

### Health Signals & Evidence Collection
When dbt tests or Dagster asset checks fail during pipeline runs, the **Health Signal Layer** (`health/`) collects evidence across:
- **dbt Test Results**: Failed test assertions, expected vs actual values, failing row counts.
- **Dagster Lineage & Asset Graph**: Upstream dependency graphs and asset execution statuses.
- **Database Statistics & Ingestion Metadata**: Row count statistics, schema structures, and batch load metadata.

These signals are normalized into typed `HealthSignal` records containing `SignalType`, `Severity`, `asset`, `test_name`, timestamps, and detailed error metadata.

### Deterministic Diagnosis Engine
The **Diagnosis Engine** (`diagnosis/`) evaluates active health signals against deterministic rules (`NullKeyRule`, `DuplicateOrderRule`, `InvalidStatusRule`, `ReferentialIntegrityRule`, `VolumeAnomalyRule`).

For example, when a `not_null` dbt test assertion fails on `stg_orders.customer_id`, the Diagnosis Engine:
1. Matches `NullKeyRule`.
2. Computes a deterministic confidence score (**0.95**).
3. Constructs a structured `Incident` object containing:
   - **Status**: `DIAGNOSED`
   - **Root Cause**: *"Upstream source data-quality regression introduced NULL customer_id values into batch orders."*
   - **Impact**: *"Downstream order analytics and customer attribution models will contain incomplete customer metrics."*
   - **Evidence**: List of failed dbt tests, target assets, and signal metadata.
   - **Recommended Remediation**: Step-by-step actions requiring human operator review.

---

## 8. Data Flow

1. **Ingestion**: `ingestion/pipeline.py` reads JSON files from `data/sample/` and loads them into PostgreSQL schema `raw_data` via `dlt`.
2. **Staging**: `stg_*` dbt models clean, type-cast, and sanitize raw fields.
3. **Intermediate**: `int_customer_orders` aggregates metrics across customers and orders.
4. **Marts**: `fct_orders`, `dim_customers`, and `dim_products` form the star-schema analytics layer.
5. **Orchestration**: Dagster triggers and monitors the end-to-end asset execution graph and executes asset quality checks.
6. **Health Aggregation & Diagnosis**: `health/aggregator.py` collects signals and `diagnosis/engine.py` generates the incident diagnosis report.

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

### Step 4: Test Failure Injection & Diagnosis
```bash
# Inject failure
dataops inject --scenario null_customer_id

# Re-run ingestion & dbt test
python -m ingestion.pipeline
make dbt-test

# Diagnose failure
dataops diagnose

# Reset to healthy pipeline
dataops reset
```

### Step 5: Run Pytest Suite
```bash
make test
# Or: .venv/bin/pytest tests/ -v
```
