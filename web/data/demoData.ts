export interface PipelineNode {
  id: string;
  name: string;
  category: string;
  status: 'HEALTHY' | 'WARNING' | 'FAILED';
  description: string;
  metadata: Record<string, string | number>;
  tech: string;
}

export interface IncidentItem {
  id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  affectedAsset: string;
  failedTest: string;
  status: 'DETECTED' | 'INVESTIGATING' | 'DIAGNOSED' | 'PENDING_APPROVAL' | 'APPROVED' | 'EXECUTING' | 'VERIFIED' | 'RESOLVED';
  createdAt: string;
}

export interface MCPToolStep {
  step: number;
  tool: string;
  purpose: string;
  status: 'SUCCESS' | 'RUNNING' | 'PENDING';
  arguments: Record<string, any>;
  resultSummary: string;
  factExtracted: string;
}

export interface RemediationActionItem {
  id: string;
  actionType: 'quarantine_invalid_records' | 'refresh_dbt_model' | 'rerun_dagster_asset';
  target: string;
  risk: 'LOW' | 'MEDIUM' | 'HIGH';
  expectedOutcome: string;
  status: 'PENDING' | 'EXECUTING' | 'SUCCESS';
}

export interface VerificationCheckItem {
  checkName: string;
  expected: string;
  actual: string;
  status: 'PASSED' | 'FAILED';
  evidence: string;
}

export const INITIAL_PIPELINE_NODES: PipelineNode[] = [
  {
    id: 'data_sources',
    name: 'Data Sources',
    category: 'Ingestion',
    status: 'HEALTHY',
    description: 'E-commerce transactional JSON batch files',
    tech: 'JSON / REST API',
    metadata: {
      'Source Datasets': 4,
      'Total Records': 505,
      'Format': 'JSON',
      'Batch Frequency': 'Hourly'
    }
  },
  {
    id: 'dlt_ingestion',
    name: 'dlt Ingestion',
    category: 'Ingestion',
    status: 'HEALTHY',
    description: 'Python dlt pipeline extracting raw JSON data into PostgreSQL',
    tech: 'dlt (data load tool)',
    metadata: {
      'Pipeline Name': 'ecommerce_ingestion',
      'Destination': 'PostgreSQL 16',
      'Target Schema': 'raw_data',
      'Write Disposition': 'replace'
    }
  },
  {
    id: 'postgres_raw',
    name: 'PostgreSQL Raw',
    category: 'Storage',
    status: 'HEALTHY',
    description: 'Relational database housing raw and transformed data tables',
    tech: 'PostgreSQL 16',
    metadata: {
      'Port': 5433,
      'Schemas': 'raw_data, staging, intermediate, marts',
      'Active Tables': 11,
      'Row Count': 525
    }
  },
  {
    id: 'dbt_transformation',
    name: 'dbt Models',
    category: 'Transformation',
    status: 'FAILED',
    description: 'Modular SQL transformations with 27 data quality assertions',
    tech: 'dbt-core / dbt-postgres',
    metadata: {
      'Models': 7,
      'Staging Views': 4,
      'Mart Tables': 3,
      'Quality Tests': 27
    }
  },
  {
    id: 'dagster_orchestrator',
    name: 'Dagster Engine',
    category: 'Orchestration',
    status: 'FAILED',
    description: 'Asset orchestration, lineage graphs, and runtime asset checks',
    tech: 'Dagster 1.6+',
    metadata: {
      'Assets Defined': 8,
      'Asset Checks': 4,
      'Failed Assets': 2,
      'Scheduler': 'Active'
    }
  },
  {
    id: 'health_signals',
    name: 'Health Signals',
    category: 'Observability',
    status: 'WARNING',
    description: 'Normalized data quality signals and evidence collectors',
    tech: 'Pydantic Signal Layer',
    metadata: {
      'Active Signals': 3,
      'Severity Level': 'HIGH',
      'Collectors': 5,
      'Signal Status': 'DEGRADED'
    }
  },
  {
    id: 'mcp_server',
    name: 'MCP Server',
    category: 'Protocol',
    status: 'HEALTHY',
    description: 'Standardized read-only & proposal tools for AI Agent interface',
    tech: 'Model Context Protocol (stdio)',
    metadata: {
      'Registered Tools': 22,
      'Transport': 'stdio',
      'Access Mode': 'Read-Only / Proposal',
      'Security Policy': 'Strict Allowlist'
    }
  },
  {
    id: 'dataops_agent',
    name: 'LLM DataOps Agent',
    category: 'AI Reasoning',
    status: 'HEALTHY',
    description: 'Autonomous DataOps engineer carrying out evidence-based diagnosis',
    tech: 'LLMProvider / Agent Loop',
    metadata: {
      'Tool Calls Budget': 15,
      'Step Budget': 10,
      'Reasoning Mode': 'Evidence-Grounded',
      'Execution Control': 'Human Approval Gate'
    }
  }
];

export const DEMO_INCIDENT: IncidentItem = {
  id: 'INC-001',
  severity: 'HIGH',
  title: 'NULL customer_id Data-Quality Regression',
  affectedAsset: 'stg_orders → fct_orders',
  failedTest: 'not_null_stg_orders_customer_id',
  status: 'DIAGNOSED',
  createdAt: '10 mins ago'
};

export const DEMO_MCP_STEPS: MCPToolStep[] = [
  {
    step: 1,
    tool: 'get_diagnosis',
    purpose: 'Retrieve active pipeline health signals and rule-based error report',
    status: 'SUCCESS',
    arguments: { incident_id: 'INC-001' },
    resultSummary: 'Retrieved diagnostic report: NULL customer_id values detected in stg_orders.',
    factExtracted: 'Signal recorded: dbt assertion failed: NULL customer_id values in stg_orders'
  },
  {
    step: 2,
    tool: 'get_failed_assets',
    purpose: 'List Dagster assets halted due to assertion failures',
    status: 'SUCCESS',
    arguments: {},
    resultSummary: 'Failed assets identified: stg_orders, fct_orders.',
    factExtracted: 'Dagster halted downstream materialization for stg_orders and fct_orders'
  },
  {
    step: 3,
    tool: 'get_failed_dbt_tests',
    purpose: 'Pinpoint exact failing dbt data quality test assertions',
    status: 'SUCCESS',
    arguments: {},
    resultSummary: 'dbt assertion failure: not_null_stg_orders_customer_id (2 failing rows).',
    factExtracted: 'not_null_stg_orders_customer_id assertion failed with 2 NULL customer_id records'
  },
  {
    step: 4,
    tool: 'get_asset_lineage',
    purpose: 'Trace upstream source dependencies and downstream asset impact',
    status: 'SUCCESS',
    arguments: { asset_name: 'stg_orders' },
    resultSummary: 'Lineage confirmed: raw_orders → stg_orders → fct_orders, daily_revenue.',
    factExtracted: 'Failure propagates downstream from raw_orders through stg_orders into fct_orders'
  },
  {
    step: 5,
    tool: 'get_column_stats',
    purpose: 'Inspect null counts and data distribution on customer_id column',
    status: 'SUCCESS',
    arguments: { table_name: 'staging.stg_orders', column_name: 'customer_id' },
    resultSummary: 'NULL ratio anomaly detected: customer_id null_count = 2 (20.0% null ratio).',
    factExtracted: 'customer_id NULL ratio surged from 0.0% baseline to 20.0%'
  },
  {
    step: 6,
    tool: 'get_ingestion_metadata',
    purpose: 'Inspect latest batch extraction metadata from source JSON dataset',
    status: 'SUCCESS',
    arguments: {},
    resultSummary: 'Batch extraction: latest raw_orders JSON payload contained unpopulated customer keys.',
    factExtracted: 'Regression originated in raw_orders batch extraction timestamp 2026-02-25T12:00:00Z'
  }
];

export const DEMO_REMEDIATION_ACTIONS: RemediationActionItem[] = [
  {
    id: 'act_01',
    actionType: 'quarantine_invalid_records',
    target: 'staging.stg_orders',
    risk: 'LOW',
    expectedOutcome: 'Move 2 invalid NULL customer_id records to staging_stg_orders_quarantine table without deleting data',
    status: 'PENDING'
  },
  {
    id: 'act_02',
    actionType: 'refresh_dbt_model',
    target: 'fct_orders',
    risk: 'MEDIUM',
    expectedOutcome: 'Re-compile and materialise fct_orders mart model with valid records',
    status: 'PENDING'
  },
  {
    id: 'act_03',
    actionType: 'rerun_dagster_asset',
    target: 'fct_orders',
    risk: 'LOW',
    expectedOutcome: 'Re-execute Dagster asset pipeline check dagster_run_fct_orders_001',
    status: 'PENDING'
  }
];

export const DEMO_VERIFICATION_CHECKS: VerificationCheckItem[] = [
  {
    checkName: 'dagster_asset_health_check',
    expected: '0 failed assets',
    actual: '0 failed assets',
    status: 'PASSED',
    evidence: 'Failed assets remaining: None'
  },
  {
    checkName: 'dbt_data_quality_tests',
    expected: '0 failing tests',
    actual: '0 failing tests',
    status: 'PASSED',
    evidence: 'All 27 dbt data quality assertions PASSED'
  },
  {
    checkName: 'null_customer_id_threshold_check',
    expected: '0 NULL rows in active transformation',
    actual: '0 NULL rows',
    status: 'PASSED',
    evidence: 'NULL customer_id records successfully quarantined in staging_stg_orders_quarantine'
  }
];

export const ARCHITECTURE_COMPONENTS = [
  {
    id: 'arch_sources',
    name: 'Data Sources',
    tech: 'JSON Datasets / REST API',
    purpose: 'Generates hourly batch transactional e-commerce data payloads.',
    responsibility: 'Provides customers, products, orders, and payments raw data streams.'
  },
  {
    id: 'arch_dlt',
    name: 'dlt Ingestion',
    tech: 'dlt (data load tool)',
    purpose: 'Extracts raw source JSON files and loads them into PostgreSQL.',
    responsibility: 'Ensures schema inference, table creation, and failure injection hook evaluation.'
  },
  {
    id: 'arch_postgres',
    name: 'PostgreSQL 16',
    tech: 'Postgres / SQL',
    purpose: 'Relational data store housing raw_data, staging, intermediate, and marts schemas.',
    responsibility: 'Serves as the single source of truth for raw batches and analytical models.'
  },
  {
    id: 'arch_dbt',
    name: 'dbt Transformations',
    tech: 'dbt-core / dbt-postgres',
    purpose: 'Compiles SQL transformations and runs 27 data quality assertions.',
    responsibility: 'Materializes staging views and analytics marts; catches null/unique/integrity violations.'
  },
  {
    id: 'arch_dagster',
    name: 'Dagster Orchestrator',
    tech: 'Dagster 1.6+',
    purpose: 'Manages software-defined assets, lineage graphs, and runtime asset checks.',
    responsibility: 'Halts downstream execution automatically upon data quality test failures.'
  },
  {
    id: 'arch_health',
    name: 'Health Signals',
    tech: 'Pydantic Signal Layer',
    purpose: 'Collects and normalizes pipeline failures, logs, and database metrics.',
    responsibility: 'Supplies normalized signal data to the diagnosis engine and evidence collectors.'
  },
  {
    id: 'arch_incident',
    name: 'Incident Engine',
    tech: 'Rule-Based Engine',
    purpose: 'Formulates initial deterministic incident records and evidence lists.',
    responsibility: 'Creates structured incidents with confidence scores prior to agent escalation.'
  },
  {
    id: 'arch_mcp',
    name: 'MCP Server',
    tech: 'Model Context Protocol (stdio)',
    purpose: 'Provides 22 typed, read-only and proposal tools over stdio transport.',
    responsibility: 'Ensures strict read-only governance and decouples AI reasoning from infrastructure.'
  },
  {
    id: 'arch_agent',
    name: 'LLM DataOps Agent',
    tech: 'Python / LLMProvider',
    purpose: 'Investigates incidents using MCP tools, collecting facts vs inferences.',
    responsibility: 'Traces asset lineage, calculates evidence confidence, and proposes remediation plans.'
  },
  {
    id: 'arch_validator',
    name: 'Action Validator',
    tech: 'Allowlist Engine',
    purpose: 'Validates proposed remediation plans against safety rules and target allowlists.',
    responsibility: 'Ensures only allowlisted actions (rerun, quarantine, refresh) can be requested.'
  },
  {
    id: 'arch_approval',
    name: 'Human Approval Gate',
    tech: 'Approval Service (TTL: 30m)',
    purpose: 'Requires explicit human operator approval before execution.',
    responsibility: 'Enforces self-approval prevention and approval TTL expiration.'
  },
  {
    id: 'arch_executor',
    name: 'Remediation Executor',
    tech: 'Controlled Executor',
    purpose: 'Executes approved allowlisted actions cleanly.',
    responsibility: 'Runs idempotent quarantines and model refreshes; records immutable audit logs.'
  },
  {
    id: 'arch_verifier',
    name: 'Recovery Verifier',
    tech: 'Verifier System',
    purpose: 'Audits post-remediation data quality test assertions and asset health.',
    responsibility: 'Transitions incident status to RESOLVED only when all checks pass.'
  }
];
