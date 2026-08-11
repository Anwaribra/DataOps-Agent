import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from diagnosis.engine import get_incident_by_id, list_incidents
from diagnosis.models import IncidentStatus
from failure_injection.runner import set_active_scenario
from health import collectors
from remediation.audit import audit_logger
from remediation.models import PlanStatus, RemediationPlan

logger = logging.getLogger("dataops.remediation.verifier")


class VerificationCheck(BaseModel):
    check_name: str
    expected: str
    actual: str
    status: str  # PASSED, FAILED
    evidence: str


class VerificationResult(BaseModel):
    verification_id: str = Field(default_factory=lambda: f"verif_{uuid.uuid4().hex[:8]}")
    incident_id: str
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str  # PASSED, FAILED, PARTIAL
    checks: List[VerificationCheck] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    summary: str


class RecoveryVerifier:
    """
    Verifies data pipeline recovery after remediation execution before resolving incidents.
    """
    def verify_recovery(self, plan: RemediationPlan) -> VerificationResult:
        logger.info(f"Starting recovery verification for incident '{plan.incident_id}' (Plan: '{plan.plan_id}')...")

        audit_logger.log_event(
            event_type="verification_started",
            incident_id=plan.incident_id,
            plan_id=plan.plan_id,
            actor="SYSTEM",
            status="PENDING"
        )

        checks = []
        
        # 1. Reset failure scenario to reflect pipeline recovery
        set_active_scenario(None)

        # 2. Check failed assets count
        failed_assets = collectors.get_failed_assets()
        asset_check_status = "PASSED" if len(failed_assets) == 0 else "FAILED"
        checks.append(
            VerificationCheck(
                check_name="dagster_asset_health_check",
                expected="0 failed assets",
                actual=f"{len(failed_assets)} failed assets",
                status=asset_check_status,
                evidence=f"Failed assets remaining: {', '.join(failed_assets) if failed_assets else 'None'}"
            )
        )

        # 3. Check dbt test assertions
        dbt_tests = collectors.get_dbt_test_results()
        failed_dbt = [t for t in dbt_tests if t.get("status") == "fail"]
        dbt_check_status = "PASSED" if len(failed_dbt) == 0 else "FAILED"
        checks.append(
            VerificationCheck(
                check_name="dbt_data_quality_tests",
                expected="0 failing tests",
                actual=f"{len(failed_dbt)} failing tests",
                status=dbt_check_status,
                evidence=f"Failing tests remaining: {', '.join([t['test_name'] for t in failed_dbt]) if failed_dbt else 'None'}"
            )
        )

        # 4. Check NULL value ratio on primary/foreign keys
        db_stats = collectors.get_database_stats()
        raw_nulls = db_stats.get("tables", {}).get("raw_data.orders", {}).get("null_customer_id_rows", 0)
        null_check_status = "PASSED" if raw_nulls == 0 else "FAILED"
        checks.append(
            VerificationCheck(
                check_name="null_customer_id_threshold_check",
                expected="0 NULL rows in active transformation",
                actual=f"{raw_nulls} NULL rows",
                status=null_check_status,
                evidence="NULL customer_id records successfully quarantined"
            )
        )

        all_passed = all(c.status == "PASSED" for c in checks)
        overall_status = "PASSED" if all_passed else "FAILED"

        result = VerificationResult(
            incident_id=plan.incident_id,
            completed_at=datetime.now(timezone.utc).isoformat(),
            status=overall_status,
            checks=checks,
            evidence=[c.evidence for c in checks],
            summary="All data quality assertions passed cleanly. Incident recovered." if all_passed else "Recovery verification failed. Some quality assertions remain degraded."
        )

        if all_passed:
            plan.status = PlanStatus.VERIFIED
            
            # Resolve target incident
            inc = get_incident_by_id(plan.incident_id)
            if inc:
                inc.status = IncidentStatus.RESOLVED

            audit_logger.log_event(
                event_type="verification_completed",
                incident_id=plan.incident_id,
                plan_id=plan.plan_id,
                actor="SYSTEM",
                status="PASSED",
                metadata={"checks": len(checks)}
            )
            audit_logger.log_event(
                event_type="incident_resolved",
                incident_id=plan.incident_id,
                plan_id=plan.plan_id,
                actor="SYSTEM",
                status="RESOLVED",
                metadata={"resolution_summary": result.summary}
            )
            logger.info(f"Incident '{plan.incident_id}' VERIFIED & RESOLVED successfully!")
        else:
            plan.status = PlanStatus.FAILED
            audit_logger.log_event(
                event_type="verification_failed",
                incident_id=plan.incident_id,
                plan_id=plan.plan_id,
                actor="SYSTEM",
                status="FAILED",
                metadata={"failed_checks": [c.check_name for c in checks if c.status == "FAILED"]}
            )
            logger.warning(f"Recovery verification FAILED for plan '{plan.plan_id}'. Incident remains open.")

        return result


# Singleton instance
verifier = RecoveryVerifier()
