import sys
from pathlib import Path
from dagster import AssetCheckResult, asset_check

DAGSTER_DIR = Path(__file__).resolve().parent.parent
if str(DAGSTER_DIR) not in sys.path:
    sys.path.insert(0, str(DAGSTER_DIR))

from assets.dbt_assets import dbt_transformation_models
from resources.db_resource import PostgresResource

@asset_check(
    asset=dbt_transformation_models,
    name="orders_row_count_check",
    description="Verifies that fct_orders fact table contains valid records"
)
def check_orders_row_count(postgres: PostgresResource) -> AssetCheckResult:
    conn = postgres.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM marts.fct_orders;")
        row_count = cursor.fetchone()[0]
        passed = row_count > 0
        return AssetCheckResult(
            passed=passed,
            metadata={
                "table": "marts.fct_orders",
                "row_count": row_count
            }
        )
    except Exception as e:
        return AssetCheckResult(
            passed=False,
            metadata={"error": str(e)}
        )
    finally:
        cursor.close()
        conn.close()
