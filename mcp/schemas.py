from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# --- Dagster Tool Schemas ---
class GetFailedAssetsInput(BaseModel):
    pass

class AssetSummary(BaseModel):
    name: str
    status: str
    last_run: str
    failure_reason: str

class GetFailedAssetsOutput(BaseModel):
    assets: List[AssetSummary]

class GetAssetStatusInput(BaseModel):
    asset_name: str = Field(description="Name of the Dagster asset (e.g. 'stg_orders', 'fct_orders')")

class GetAssetStatusOutput(BaseModel):
    asset_name: str
    status: str
    last_successful_run: Optional[str] = None
    last_failed_run: Optional[str] = None
    latest_run: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GetAssetLineageInput(BaseModel):
    asset_name: str = Field(description="Target asset name to trace lineage for")

class GetAssetLineageOutput(BaseModel):
    asset: str
    upstream: List[str]
    downstream: List[str]

class GetRecentRunsInput(BaseModel):
    asset_name: str = Field(description="Asset name to query execution history")
    limit: int = Field(default=5, ge=1, le=50, description="Maximum number of recent runs to return")

class RunSummary(BaseModel):
    run_id: str
    asset: str
    status: str
    timestamp: str

class GetRecentRunsOutput(BaseModel):
    asset_name: str
    runs: List[RunSummary]

class GetAssetChecksInput(BaseModel):
    asset_name: str = Field(description="Asset name to inspect quality checks for")

class AssetCheckDetail(BaseModel):
    check_name: str
    asset_name: str
    status: str
    description: str

class GetAssetChecksOutput(BaseModel):
    asset_name: str
    checks: List[AssetCheckDetail]


# --- dbt Tool Schemas ---
class GetDbtTestResultsInput(BaseModel):
    pass

class DbtTestDetail(BaseModel):
    name: str
    model: str
    status: str
    failures: int
    message: Optional[str] = None

class GetDbtTestResultsOutput(BaseModel):
    tests: List[DbtTestDetail]

class GetDbtModelStatusInput(BaseModel):
    model_name: str = Field(description="Target dbt model name (e.g., 'stg_orders', 'fct_orders')")

class GetDbtModelStatusOutput(BaseModel):
    model_name: str
    status: str
    materialization: str
    schema_name: str
    columns: List[str]

class GetFailedDbtTestsInput(BaseModel):
    pass

class GetFailedDbtTestsOutput(BaseModel):
    failed_tests: List[DbtTestDetail]


# --- Incident Tool Schemas ---
class ListIncidentsInput(BaseModel):
    pass

class IncidentSummary(BaseModel):
    incident_id: str
    status: str
    severity: str
    detected_at: str
    affected_assets: List[str]
    probable_root_cause: str
    confidence: float

class ListIncidentsOutput(BaseModel):
    incidents: List[IncidentSummary]

class GetIncidentInput(BaseModel):
    incident_id: str = Field(description="Unique incident ID to retrieve")

class GetIncidentOutput(BaseModel):
    incident: Dict[str, Any]

class GetIncidentEvidenceInput(BaseModel):
    incident_id: str = Field(description="Unique incident ID to inspect evidence for")

class GetIncidentEvidenceOutput(BaseModel):
    incident_id: str
    evidence: List[str]

class GetDiagnosisInput(BaseModel):
    incident_id: Optional[str] = Field(default=None, description="Optional incident ID to diagnose")

class GetDiagnosisOutput(BaseModel):
    incident_id: str
    status: str
    severity: str
    affected_assets: List[str]
    root_cause: str
    confidence: float
    evidence: List[str]
    impact: str
    recommended_actions: List[str]


# --- Database Tool Schemas ---
class GetTableStatsInput(BaseModel):
    table_name: str = Field(description="Allowed table name (e.g., 'staging.stg_orders', 'marts.fct_orders')")

class GetTableStatsOutput(BaseModel):
    table_name: str
    row_count: int
    schema_name: str
    is_allowed: bool

class GetColumnStatsInput(BaseModel):
    table_name: str = Field(description="Allowed table name")
    column_name: str = Field(description="Target column name")

class GetColumnStatsOutput(BaseModel):
    table_name: str
    column_name: str
    data_type: str
    null_count: int
    distinct_count: int

class GetRecentDataQualityStatsInput(BaseModel):
    table_name: str = Field(description="Target table name for quality metrics")

class GetRecentDataQualityStatsOutput(BaseModel):
    table_name: str
    total_rows: int
    quality_score: float
    issues_detected: List[str]


# --- Ingestion Tool Schemas ---
class GetIngestionStatusInput(BaseModel):
    pass

class GetIngestionStatusOutput(BaseModel):
    pipeline_name: str
    status: str
    last_run_timestamp: str
    destination: str

class GetIngestionMetadataInput(BaseModel):
    pass

class GetIngestionMetadataOutput(BaseModel):
    pipeline: str
    active_scenario: str
    last_ingestion_timestamp: str
    records_ingested: Dict[str, int]


# Generic Error Output
class MCPErrorResponse(BaseModel):
    error: str
    tool_name: str
    requested_input: Dict[str, Any] = Field(default_factory=dict)
