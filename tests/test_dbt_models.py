import os
from pathlib import Path

DBT_DIR = Path(__file__).resolve().parent.parent / "dbt"

def test_dbt_files_exist():
    assert (DBT_DIR / "dbt_project.yml").exists()
    assert (DBT_DIR / "profiles.yml").exists()
    assert (DBT_DIR / "models" / "staging" / "stg_customers.sql").exists()
    assert (DBT_DIR / "models" / "staging" / "stg_orders.sql").exists()
    assert (DBT_DIR / "models" / "intermediate" / "int_customer_orders.sql").exists()
    assert (DBT_DIR / "models" / "marts" / "fct_orders.sql").exists()
    assert (DBT_DIR / "models" / "marts" / "dim_customers.sql").exists()

def test_dbt_schema_files_exist():
    assert (DBT_DIR / "models" / "staging" / "schema.yml").exists()
    assert (DBT_DIR / "models" / "intermediate" / "schema.yml").exists()
    assert (DBT_DIR / "models" / "marts" / "schema.yml").exists()
