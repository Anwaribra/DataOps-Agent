import sys
from pathlib import Path
from dagster import Definitions, define_asset_job, load_assets_from_modules

DAGSTER_DIR = Path(__file__).resolve().parent
if str(DAGSTER_DIR) not in sys.path:
    sys.path.insert(0, str(DAGSTER_DIR))

from assets import dbt_assets, ingestion_assets
from checks.quality_checks import check_orders_row_count
from resources.db_resource import PostgresResource

all_assets = [
    *load_assets_from_modules([ingestion_assets]),
    *load_assets_from_modules([dbt_assets])
]

ecommerce_pipeline_job = define_asset_job(
    name="ecommerce_dataops_pipeline",
    selection=["raw_ecommerce_data", "dbt_transformation_models", "dbt_test_results"]
)

defs = Definitions(
    assets=all_assets,
    asset_checks=[check_orders_row_count],
    jobs=[ecommerce_pipeline_job],
    resources={
        "postgres": PostgresResource()
    }
)
