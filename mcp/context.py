import logging
import os
import psycopg2
from typing import Any, Dict, List, Optional
from diagnosis.engine import DiagnosisEngine, get_incident_by_id, list_incidents
from health import collectors

logger = logging.getLogger("dataops.mcp.context")

ALLOWED_SCHEMAS = {"raw_data", "staging", "intermediate", "marts"}
ALLOWED_TABLES = {
    "raw_data.customers", "raw_data.products", "raw_data.orders", "raw_data.payments",
    "staging.stg_customers", "staging.stg_products", "staging.stg_orders", "staging.stg_payments",
    "intermediate.int_customer_orders",
    "marts.fct_orders", "marts.dim_customers", "marts.dim_products"
}

class MCPApplicationContext:
    def __init__(self):
        self.db_host = os.getenv("POSTGRES_HOST", "localhost")
        self.db_port = int(os.getenv("POSTGRES_PORT", "5433"))
        self.db_user = os.getenv("POSTGRES_USER", "dataops_user")
        self.db_password = os.getenv("POSTGRES_PASSWORD", "dataops_password")
        self.db_name = os.getenv("POSTGRES_DB", "dataops_db")
        self._diagnosis_engine = DiagnosisEngine()

    def get_db_connection(self):
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_password,
            dbname=self.db_name
        )

    # Health & Evidence Collectors wrappers
    def get_failed_assets(self) -> List[str]:
        return collectors.get_failed_assets()

    def get_asset_lineage(self, asset_name: str) -> Dict[str, Any]:
        return collectors.get_asset_lineage(asset_name)

    def get_recent_runs(self, asset_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        runs = collectors.get_recent_runs(asset_name)
        return runs[:limit]

    def get_dbt_test_results(self) -> List[Dict[str, Any]]:
        return collectors.get_dbt_test_results()

    def get_ingestion_metadata(self) -> Dict[str, Any]:
        return collectors.get_ingestion_metadata()

    def get_database_stats(self) -> Dict[str, Any]:
        return collectors.get_database_stats()

    # Incident System wrappers
    def list_incidents(self) -> List[Any]:
        return list_incidents()

    def get_incident(self, incident_id: str) -> Optional[Any]:
        return get_incident_by_id(incident_id)

    def get_diagnosis(self, incident_id: Optional[str] = None) -> Any:
        if incident_id:
            inc = get_incident_by_id(incident_id)
            if inc:
                return inc
        return self._diagnosis_engine.diagnose_active_pipeline()

    # Safe Read-Only Database Queries
    def is_table_allowed(self, table_name: str) -> bool:
        clean_name = table_name.strip().lower()
        if clean_name in ALLOWED_TABLES:
            return True
        # Allow unqualified table names if they exist in allowed tables
        for allowed in ALLOWED_TABLES:
            if allowed.endswith(f".{clean_name}"):
                return True
        return False

    def get_table_row_count(self, table_name: str) -> int:
        if not self.is_table_allowed(table_name):
            raise ValueError(f"Access denied: table '{table_name}' is not in approved read-only registry.")
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            # Table name is validated against strict whitelist to prevent SQL injection
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            logger.error(f"Error querying table row count for {table_name}: {e}")
            return -1
        finally:
            cursor.close()
            conn.close()

# Shared singleton instance
context = MCPApplicationContext()
