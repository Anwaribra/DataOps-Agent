# DataOps Agent Architecture Overview

DataOps Agent is designed as a batch-oriented, production-style DataOps platform capable of monitoring batch data pipelines, detecting data quality failures, and assisting in incident diagnosis and remediation.

## Target End-to-End Architecture Flow

```
+---------------------+
| External Data Source| (JSON Sample Datasets)
+----------+----------+
           |
           v
+---------------------+
|    dlt Ingestion    | (Python + dlt Postgres Destination)
+----------+----------+
           |
           v
+---------------------+
| PostgreSQL Raw Layer| (schema: raw_data)
+----------+----------+
           |
           v
+---------------------+
|      dbt Layer      | (staging -> intermediate -> marts)
+----------+----------+
           |
           v
+---------------------+
|  Dagster Framework  | (Assets, Lineage, Asset Checks)
+----------+----------+
           |
           v
+---------------------+
|   DataOps Agent     | (Phase 2: LLM Reasoning)
+----------+----------+
           |
           v
+---------------------+
|     MCP Server      | (Phase 2: Controlled Tool Execution)
+----------+----------+
           |
           v
+---------------------+
| Human Approval Gate | (Remediation Plan Execution)
+---------------------+
```

## Core Components

### 1. Ingestion (`ingestion/`)
- Powered by `dlt` (data load tool).
- Extracts e-commerce datasets (`customers`, `products`, `orders`, `payments`).
- Loads raw JSON records directly into PostgreSQL database schema `raw_data`.
- Includes failure injection parameters to simulate real-world data corruption.

### 2. Database (PostgreSQL)
- Serves as the central data store containing raw schemas (`raw_data`), staging views (`staging`), intermediate transformation models (`intermediate`), and analytical fact/dimension tables (`marts`).

### 3. Transformation & Data Quality (`dbt/`)
- Staging models clean and type-cast raw data fields.
- Intermediate models aggregate customer order metrics.
- Mart models construct dimensional models (`fct_orders`, `dim_customers`, `dim_products`).
- Rigorous dbt tests enforce constraints (`unique`, `not_null`, `relationships`, `accepted_values`).

### 4. Orchestration (`dagster/`)
- Dagster definitions manage asset lineage and execution graph (`raw_ecommerce_data` -> `dbt_transformation_models` -> `dbt_test_results`).
- Dagster Asset Checks validate business rule assertions and row count metrics.

### 5. Agent & MCP Layer (Phase 2 Roadmap)
- MCP server exposes read-only diagnostic tools (Dagster run inspection, dbt test error logs, SQL queries).
- LLM agent analyzes root causes and formulates remediation proposals without executing unapproved state modifications.
