# Model Context Protocol (MCP) Server Reference

The **DataOps MCP Server** provides a controlled, secure, read-only interface through which AI diagnostic agents can inspect data pipeline states, Dagster asset graphs, dbt test assertions, database statistics, and incident reports without direct infrastructure coupling or unapproved state mutations.

---

## Why MCP?

The Model Context Protocol (MCP) establishes a standardized contract between LLM-based reasoning agents and technical platforms. 

Using MCP guarantees:
- **Decoupled Architecture**: AI reasoning agents interact through explicit, typed schemas rather than execution script hacks.
- **Strict Read-Only Governance**: The agent can inspect state, trace lineage, and read test failures, but **cannot** execute arbitrary SQL or unapproved shell commands.
- **Deterministic Reliability**: Grounding AI queries in structured evidence collected directly from Postgres, dbt artifacts, and Dagster.

---

## Available MCP Tools

| Tool Name | Purpose | Access Level |
|---|---|---|
| `get_failed_assets` | Returns currently failed Dagster assets and failure reasons | Read-Only |
| `get_asset_status` | Inspects current status, latest successful run, and metadata for an asset | Read-Only |
| `get_asset_lineage` | Traces upstream and downstream dependency graphs for an asset | Read-Only |
| `get_recent_runs` | Retrieves recent execution run history for an asset | Read-Only |
| `get_asset_checks` | Inspects Dagster asset quality checks and row count metrics | Read-Only |
| `get_dbt_test_results` | Retrieves all dbt data quality test results across the project | Read-Only |
| `get_dbt_model_status` | Inspects target dbt model compilation, schema, and materialization | Read-Only |
| `get_failed_dbt_tests` | Retrieves ONLY failed dbt test records for active incident analysis | Read-Only |
| `list_incidents` | Lists all detected pipeline incidents recorded by the platform | Read-Only |
| `get_incident` | Retrieves complete incident details by incident ID | Read-Only |
| `get_incident_evidence` | Inspects collected error evidence statements for an incident | Read-Only |
| `get_diagnosis` | Retrieves deterministic diagnosis reports containing root cause & actions | Read-Only |
| `get_table_stats` | Inspects row counts and schema info for approved database tables | Read-Only (Restricted) |
| `get_column_stats` | Inspects column data types, null counts, and cardinality | Read-Only (Restricted) |
| `get_recent_data_quality_stats` | Retrieves table quality scores and quality assertion histories | Read-Only (Restricted) |
| `get_ingestion_status` | Inspects dlt ingestion pipeline execution status and timestamps | Read-Only |
| `get_ingestion_metadata` | Retrieves ingested record counts per source file and active scenarios | Read-Only |

---

## Security Model

1. **Strict Read-Only Operations**: Write, update, drop, delete, and shell execution capabilities are disabled.
2. **No Arbitrary SQL Execution**: The generic `execute_sql` pattern is explicitly forbidden. Table queries are restricted to an approved registry (`raw_data.*`, `staging.*`, `intermediate.*`, `marts.*`).
3. **Secret Masking**: Connection credentials and sensitive API keys are filtered out of all tool responses.
4. **Input Validation**: All tool arguments are strictly validated against Pydantic schemas. Invalid inputs return structured error objects.

---

## Local Startup & Integration

### Start Server via CLI
```bash
dataops mcp start
# Or using python module runner:
python -m mcp.server
# Or using Makefile shortcut:
make mcp
```

### Transport
The server operates over standard I/O (`stdio`) transport, adhering to standard MCP client specification.
