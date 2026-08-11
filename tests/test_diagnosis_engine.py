import pytest
from failure_injection.scenarios import set_active_scenario
from diagnosis.engine import DiagnosisEngine
from diagnosis.models import IncidentStatus, Incident
from diagnosis.rules import RULES, NullKeyRule, DuplicateOrderRule, InvalidStatusRule, ReferentialIntegrityRule, VolumeAnomalyRule

def test_diagnosis_rules_definitions():
    assert len(RULES) == 5

def test_diagnosis_healthy_pipeline():
    set_active_scenario(None)
    engine = DiagnosisEngine()
    incident = engine.diagnose_active_pipeline()

    assert isinstance(incident, Incident)
    assert incident.status == IncidentStatus.RESOLVED
    assert incident.confidence == 1.0
    assert incident.severity.value == "low"

def test_diagnosis_null_customer_id_scenario():
    set_active_scenario("null_customer_id")
    engine = DiagnosisEngine()
    incident = engine.diagnose_active_pipeline()

    assert incident.status == IncidentStatus.DIAGNOSED
    assert incident.confidence == 0.95
    assert "NULL customer_id" in incident.probable_root_cause
    assert len(incident.evidence) > 0
    assert len(incident.recommended_actions) > 0
    set_active_scenario(None)

def test_diagnosis_duplicate_order_scenario():
    set_active_scenario("duplicate_order_id")
    engine = DiagnosisEngine()
    incident = engine.diagnose_active_pipeline()

    assert incident.status == IncidentStatus.DIAGNOSED
    assert incident.confidence == 0.92
    assert "duplicate order_id" in incident.probable_root_cause
    set_active_scenario(None)

def test_diagnosis_invalid_status_scenario():
    set_active_scenario("invalid_status")
    engine = DiagnosisEngine()
    incident = engine.diagnose_active_pipeline()

    assert incident.status == IncidentStatus.DIAGNOSED
    assert incident.confidence == 0.90
    assert "UNKNOWN_STATUS" in incident.probable_root_cause
    set_active_scenario(None)

def test_diagnosis_referential_integrity_scenario():
    set_active_scenario("referential_integrity")
    engine = DiagnosisEngine()
    incident = engine.diagnose_active_pipeline()

    assert incident.status == IncidentStatus.DIAGNOSED
    assert incident.confidence == 0.93
    assert "Orphan records detected" in incident.probable_root_cause
    set_active_scenario(None)

def test_diagnosis_volume_anomaly_scenario():
    set_active_scenario("volume_anomaly")
    engine = DiagnosisEngine()
    incident = engine.diagnose_active_pipeline()

    assert incident.status == IncidentStatus.DIAGNOSED
    assert incident.confidence == 0.88
    assert "Abnormal volume spike" in incident.probable_root_cause
    set_active_scenario(None)
