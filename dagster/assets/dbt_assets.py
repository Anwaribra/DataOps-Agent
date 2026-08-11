import os
import subprocess
from pathlib import Path
from dagster import MaterializeResult, MetadataValue, asset

DBT_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent / "dbt"

@asset(
    deps=["raw_ecommerce_data"],
    group_name="transformation",
    description="Executes dbt transformation models (staging, intermediate, marts) in PostgreSQL"
)
def dbt_transformation_models() -> MaterializeResult:
    cmd = ["dbt", "run", "--profiles-dir", str(DBT_PROJECT_DIR), "--project-dir", str(DBT_PROJECT_DIR)]
    env = os.environ.copy()
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise Exception(f"dbt run failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

    return MaterializeResult(
        metadata={
            "dbt_project": "dataops_dbt",
            "command": "dbt run",
            "output_preview": MetadataValue.text(result.stdout[-500:])
        }
    )

@asset(
    deps=["dbt_transformation_models"],
    group_name="data_quality",
    description="Executes dbt data quality tests (unique, not_null, accepted_values, relationships)"
)
def dbt_test_results() -> MaterializeResult:
    cmd = ["dbt", "test", "--profiles-dir", str(DBT_PROJECT_DIR), "--project-dir", str(DBT_PROJECT_DIR)]
    env = os.environ.copy()
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise Exception(f"dbt test failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

    return MaterializeResult(
        metadata={
            "dbt_project": "dataops_dbt",
            "command": "dbt test",
            "status": "all_tests_passed",
            "output_preview": MetadataValue.text(result.stdout[-500:])
        }
    )
