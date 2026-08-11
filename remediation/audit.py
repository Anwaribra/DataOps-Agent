import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("dataops.remediation.audit")

BASE_DIR = Path(__file__).resolve().parent.parent
AUDIT_LOG_FILE = BASE_DIR / "docs" / "remediation_audit.jsonl"


class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    incident_id: str
    plan_id: Optional[str] = None
    event_type: str
    actor: str  # AGENT, HUMAN, SYSTEM
    status: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AuditLogger:
    """
    Appends structured, immutable audit log events for all remediation and approval operations.
    """
    def __init__(self, log_path: Path = AUDIT_LOG_FILE):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(
        self,
        event_type: str,
        incident_id: str,
        actor: str,
        status: str,
        plan_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        event = AuditEvent(
            incident_id=incident_id,
            plan_id=plan_id,
            event_type=event_type,
            actor=actor,
            status=status,
            metadata=metadata or {}
        )
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(event.model_dump_json() + "\n")
            logger.info(f"Audit Log [{event_type}]: incident={incident_id}, actor={actor}, status={status}")
        except Exception as e:
            logger.error(f"Failed to write audit log event: {e}")
        return event

    def get_events_for_incident(self, incident_id: str) -> List[AuditEvent]:
        if not self.log_path.exists():
            return []
        events = []
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if data.get("incident_id") == incident_id:
                            events.append(AuditEvent(**data))
        except Exception as e:
            logger.error(f"Failed to read audit log events: {e}")
        return events


# Shared singleton instance
audit_logger = AuditLogger()
