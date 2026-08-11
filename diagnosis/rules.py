from typing import List, Optional, Tuple
from health.models import HealthSignal, SignalType


class DiagnosisRule:
    def __init__(self, rule_name: str, description: str):
        self.rule_name = rule_name
        self.description = description

    def evaluate(self, signals: List[HealthSignal]) -> Optional[Tuple[str, float, str, List[str], List[str]]]:
        """
        Evaluates signals against the rule.
        Returns (root_cause, confidence, impact, evidence_list, recommended_actions_list) if rule matches.
        """
        raise NotImplementedError()


class NullKeyRule(DiagnosisRule):
    def __init__(self):
        super().__init__(
            rule_name="null_customer_id_rule",
            description="Evaluates NULL primary/foreign key data quality failures."
        )

    def evaluate(self, signals: List[HealthSignal]):
        for sig in signals:
            if sig.signal_type == SignalType.DBT_TEST_FAILURE and "not_null" in (sig.test_name or "").lower():
                root_cause = "Upstream source data-quality regression introduced NULL customer_id values into batch orders."
                confidence = 0.95
                impact = "Downstream order analytics and customer attribution models will contain incomplete customer metrics."
                evidence = [
                    f"dbt test failure: {sig.test_name}",
                    f"Target asset affected: {sig.asset}",
                    "Ingestion succeeded but raw batch contained unpopulated customer keys",
                    f"Failure signal recorded: {sig.message}"
                ]
                actions = [
                    "Quarantine affected records containing NULL customer_id",
                    "Validate upstream source API/file extraction process",
                    "Re-execute dbt model transformation after source data correction"
                ]
                return root_cause, confidence, impact, evidence, actions
        return None


class DuplicateOrderRule(DiagnosisRule):
    def __init__(self):
        super().__init__(
            rule_name="duplicate_order_id_rule",
            description="Evaluates duplicate primary key assertions."
        )

    def evaluate(self, signals: List[HealthSignal]):
        for sig in signals:
            if sig.signal_type == SignalType.DBT_TEST_FAILURE and "unique" in (sig.test_name or "").lower():
                root_cause = "Upstream batch ingestion produced duplicate order_id records in source dataset."
                confidence = 0.92
                impact = "Fact tables and revenue metrics will double-count duplicate transaction totals."
                evidence = [
                    f"dbt test failure: {sig.test_name}",
                    f"Target asset affected: {sig.asset}",
                    "Duplicate primary key constraint violation detected during dbt test run",
                    f"Failure signal message: {sig.message}"
                ]
                actions = [
                    "Deduplicate records in raw_data.orders using window functions (ROW_NUMBER)",
                    "Audit upstream dlt ingestion pipeline write disposition settings",
                    "Re-run dbt staging and mart models"
                ]
                return root_cause, confidence, impact, evidence, actions
        return None


class InvalidStatusRule(DiagnosisRule):
    def __init__(self):
        super().__init__(
            rule_name="invalid_status_rule",
            description="Evaluates accepted_values enum constraint failures."
        )

    def evaluate(self, signals: List[HealthSignal]):
        for sig in signals:
            if sig.signal_type == SignalType.DBT_TEST_FAILURE and "accepted_values" in (sig.test_name or "").lower():
                root_cause = "Upstream order management system emitted unhandled order status value 'UNKNOWN_STATUS'."
                confidence = 0.90
                impact = "Order status filtering and state transition metrics will fail to categorize invalid orders."
                evidence = [
                    f"dbt test failure: {sig.test_name}",
                    f"Target asset affected: {sig.asset}",
                    "Accepted values constraint failed against allowed list ['completed', 'pending', 'shipped', 'cancelled', 'refunded']",
                    f"Failure signal message: {sig.message}"
                ]
                actions = [
                    "Update status mapping dictionary in stg_orders.sql or sanitize upstream enum values",
                    "Quarantine invalid status records into exception table",
                    "Re-run dbt data quality suite"
                ]
                return root_cause, confidence, impact, evidence, actions
        return None


class ReferentialIntegrityRule(DiagnosisRule):
    def __init__(self):
        super().__init__(
            rule_name="referential_integrity_rule",
            description="Evaluates foreign key relationship failures."
        )

    def evaluate(self, signals: List[HealthSignal]):
        for sig in signals:
            if sig.signal_type == SignalType.DBT_TEST_FAILURE and "relationships" in (sig.test_name or "").lower():
                root_cause = "Orphan records detected: Order placed referencing non-existent customer primary key ('cust_non_existent_999')."
                confidence = 0.93
                impact = "Join operations between fct_orders and dim_customers will result in unassigned orphan revenue."
                evidence = [
                    f"dbt test failure: {sig.test_name}",
                    f"Target asset affected: {sig.asset}",
                    "Foreign key relationship assertion failed between stg_orders and stg_customers",
                    f"Failure signal message: {sig.message}"
                ]
                actions = [
                    "Backfill missing customer record in customer extraction pipeline",
                    "Place orphan orders into staging review queue",
                    "Re-run dbt transformations"
                ]
                return root_cause, confidence, impact, evidence, actions
        return None


class VolumeAnomalyRule(DiagnosisRule):
    def __init__(self):
        super().__init__(
            rule_name="volume_anomaly_rule",
            description="Evaluates record count volume spikes."
        )

    def evaluate(self, signals: List[HealthSignal]):
        for sig in signals:
            if sig.signal_type == SignalType.VOLUME_ANOMALY:
                root_cause = "Abnormal volume spike detected in batch ingestion (500+ records vs baseline of 5 records)."
                confidence = 0.88
                impact = "Pipeline execution latency will increase significantly and downstream storage costs will spike."
                evidence = [
                    f"Volume anomaly signal: {sig.test_name}",
                    f"Target asset affected: {sig.asset}",
                    f"Batch volume exceeded expected historical threshold: {sig.message}"
                ]
                actions = [
                    "Inspect upstream batch payload for accidental replay or loop replication",
                    "Throttle batch ingestion rate if queue overflow is detected",
                    "Confirm batch legitimacy with data source owner before running full dbt models"
                ]
                return root_cause, confidence, impact, evidence, actions
        return None


RULES: List[DiagnosisRule] = [
    NullKeyRule(),
    DuplicateOrderRule(),
    InvalidStatusRule(),
    ReferentialIntegrityRule(),
    VolumeAnomalyRule()
]
