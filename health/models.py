from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field


class SignalType(str, Enum):
    DAGSTER_ASSET_FAILURE = "dagster_asset_failure"
    DAGSTER_ASSET_CHECK_FAILURE = "dagster_asset_check_failure"
    DBT_TEST_FAILURE = "dbt_test_failure"
    INGESTION_FAILURE = "ingestion_failure"
    SCHEMA_CHANGE = "schema_change"
    VOLUME_ANOMALY = "volume_anomaly"
    DATABASE_ANOMALY = "database_anomaly"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HealthSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:8]}")
    signal_type: SignalType
    severity: Severity
    asset: str
    test_name: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
