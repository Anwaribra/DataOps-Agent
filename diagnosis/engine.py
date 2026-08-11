import logging
from typing import List, Optional
from health.aggregator import collect_health_signals
from health.collectors import get_failed_assets
from health.models import HealthSignal, Severity
from diagnosis.models import Incident, IncidentStatus
from diagnosis.rules import RULES

logger = logging.getLogger(__name__)

# Simple in-memory incident repository
_INCIDENT_STORE: List[Incident] = []


class DiagnosisEngine:
    def __init__(self):
        self.rules = RULES

    def diagnose_active_pipeline(self) -> Incident:
        signals: List[HealthSignal] = collect_health_signals()
        affected_assets = get_failed_assets() or (list({sig.asset for sig in signals}) if signals else [])

        if not signals:
            logger.info("No failure signals detected. Pipeline is healthy.")
            incident = Incident(
                status=IncidentStatus.RESOLVED,
                severity=Severity.LOW,
                affected_assets=[],
                signals=[],
                evidence=["All dbt data quality tests passed", "Ingestion volume within normal baseline"],
                probable_root_cause="No root cause identified. Platform operating normally.",
                confidence=1.0,
                impact="None. Pipeline functioning as expected.",
                recommended_actions=["Maintain normal scheduled execution"]
            )
            _INCIDENT_STORE.append(incident)
            return incident

        # Evaluate rules against signals
        for rule in self.rules:
            res = rule.evaluate(signals)
            if res:
                root_cause, confidence, impact, evidence, actions = res
                incident = Incident(
                    status=IncidentStatus.DIAGNOSED,
                    severity=Severity.HIGH,
                    affected_assets=affected_assets,
                    signals=signals,
                    evidence=evidence,
                    probable_root_cause=root_cause,
                    confidence=confidence,
                    impact=impact,
                    recommended_actions=actions
                )
                _INCIDENT_STORE.append(incident)
                return incident

        # Default fallback if signals exist but no rule matched
        incident = Incident(
            status=IncidentStatus.INVESTIGATING,
            severity=Severity.MEDIUM,
            affected_assets=affected_assets,
            signals=signals,
            evidence=[sig.message for sig in signals],
            probable_root_cause="Uncategorized pipeline anomaly detected",
            confidence=0.50,
            impact="Potential downstream data quality degradation",
            recommended_actions=["Manual inspection of Dagster and dbt execution logs recommended"]
        )
        _INCIDENT_STORE.append(incident)
        return incident


def list_incidents() -> List[Incident]:
    if not _INCIDENT_STORE:
        # Trigger an evaluation if store is empty
        engine = DiagnosisEngine()
        engine.diagnose_active_pipeline()
    return _INCIDENT_STORE


def get_incident_by_id(incident_id: str) -> Optional[Incident]:
    incidents = list_incidents()
    for inc in incidents:
        if inc.incident_id == incident_id:
            return inc
    return None
