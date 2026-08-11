# Incident Report: Volume Anomaly

## 1. Incident
- **ID**: `inc_volume_anomaly_004`
- **Severity**: HIGH
- **Affected Assets**: `raw_orders`, `stg_orders`

## 2. Trigger
- **Command**: `python -m failure_injection.runner --scenario volume_anomaly`
- **Mechanism**: Ingestion payload contains 500+ order records in a single batch (baseline: 5 records).

## 3. Signals
- `SignalType.VOLUME_ANOMALY` (Severity: HIGH)
- **Test Name**: `volume_threshold_exceeded`
- **Asset**: `raw_orders`

## 4. Evidence
- Ingested 505 order records compared to historical baseline threshold of 5 records.
- Batch payload volume exceeded expected limits by 100x.

## 5. Root Cause
Abnormal volume spike detected in batch ingestion due to payload loop replication or stream replay.

## 6. Impact
Pipeline execution latency increases significantly and storage resource consumption spikes.

## 7. Recommended Remediation
1. Inspect upstream batch payload for accidental loop replication or stream replay.
2. Throttle batch ingestion queue if overflow is detected.
3. Confirm batch legitimacy with data owner before running full dbt transformations.

## 8. Expected System Behavior
- Volume collector flags abnormal volume signal.
- Diagnosis Engine matches `VolumeAnomalyRule` with **88% confidence**.
- Platform highlights record count anomaly and recommends payload review.
