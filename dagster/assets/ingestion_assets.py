import logging
from dagster import AssetMaterialization, MaterializeResult, MetadataValue, asset
from ingestion.pipeline import run_ingestion_pipeline

logger = logging.getLogger(__name__)

@asset(
    group_name="ingestion",
    description="Ingests raw e-commerce sample datasets (customers, products, orders, payments) into PostgreSQL via dlt"
)
def raw_ecommerce_data() -> MaterializeResult:
    logger.info("Executing dlt ingestion asset...")
    load_info = run_ingestion_pipeline()
    
    return MaterializeResult(
        metadata={
            "pipeline_name": "ecommerce_ingestion",
            "destination": "postgres",
            "status": "success",
            "dataset": "raw_data"
        }
    )
