import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import dlt
from dotenv import load_dotenv
from failure_injection.scenarios import apply_scenario_transformations

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DATA_DIR = BASE_DIR / "data" / "sample"


def load_sample_file(filename: str) -> List[Dict[str, Any]]:
    file_path = SAMPLE_DATA_DIR / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Sample data file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@dlt.resource(name="customers", write_disposition="replace")
def get_customers(inject_null_customer: bool = False) -> List[Dict[str, Any]]:
    customers = load_sample_file("customers.json")
    if inject_null_customer and len(customers) > 0:
        logger.warning("[Failure Injection] Injecting null customer_id into customer record.")
        customers.append({
            "customer_id": None,
            "first_name": "Corrupted",
            "last_name": "User",
            "email": "corrupted@example.com",
            "created_at": "2026-02-20T00:00:00Z",
            "status": "active"
        })
    return apply_scenario_transformations("customers", customers)


@dlt.resource(name="products", write_disposition="replace")
def get_products() -> List[Dict[str, Any]]:
    products = load_sample_file("products.json")
    return apply_scenario_transformations("products", products)


@dlt.resource(name="orders", write_disposition="replace")
def get_orders(
    inject_duplicate_orders: bool = False,
    inject_invalid_status: bool = False
) -> List[Dict[str, Any]]:
    orders = load_sample_file("orders.json")
    if inject_duplicate_orders and len(orders) > 0:
        logger.warning("[Failure Injection] Injecting duplicate order_id into orders dataset.")
        dup_order = orders[0].copy()
        dup_order["order_date"] = "2026-02-21T10:00:00Z"
        orders.append(dup_order)
    
    if inject_invalid_status and len(orders) > 0:
        logger.warning("[Failure Injection] Injecting invalid order status into orders dataset.")
        corrupted_order = orders[1].copy()
        corrupted_order["order_id"] = "ord_corrupted_999"
        corrupted_order["status"] = "INVALID_STATUS_UNKNOWN"
        orders.append(corrupted_order)

    return apply_scenario_transformations("orders", orders)


@dlt.resource(name="payments", write_disposition="replace")
def get_payments() -> List[Dict[str, Any]]:
    payments = load_sample_file("payments.json")
    return apply_scenario_transformations("payments", payments)


def get_postgres_destination_credentials() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5433")
    user = os.getenv("POSTGRES_USER", "dataops_user")
    password = os.getenv("POSTGRES_PASSWORD", "dataops_password")
    dbname = os.getenv("POSTGRES_DB", "dataops_db")
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def run_ingestion_pipeline(
    dataset_name: str = "raw_data",
    inject_duplicate_orders: bool = False,
    inject_null_customer: bool = False,
    inject_invalid_status: bool = False
) -> Any:
    logger.info("Initializing dlt ingestion pipeline...")
    credentials = get_postgres_destination_credentials()

    pipeline = dlt.pipeline(
        pipeline_name="ecommerce_ingestion",
        destination=dlt.destinations.postgres(credentials),
        dataset_name=dataset_name,
    )

    resources = [
        get_customers(inject_null_customer=inject_null_customer),
        get_products(),
        get_orders(
            inject_duplicate_orders=inject_duplicate_orders,
            inject_invalid_status=inject_invalid_status
        ),
        get_payments()
    ]

    logger.info("Extracting and loading e-commerce resources into PostgreSQL...")
    load_info = pipeline.run(resources)
    logger.info(f"Ingestion completed successfully: {load_info}")
    return load_info


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run DataOps Agent dlt Ingestion Pipeline")
    parser.add_argument("--inject-duplicate-orders", action="store_true", help="Inject duplicate order IDs")
    parser.add_argument("--inject-null-customer", action="store_true", help="Inject null customer ID")
    parser.add_argument("--inject-invalid-status", action="store_true", help="Inject invalid order status")
    args = parser.parse_args()

    run_ingestion_pipeline(
        inject_duplicate_orders=args.inject_duplicate_orders,
        inject_null_customer=args.inject_null_customer,
        inject_invalid_status=args.inject_invalid_status
    )
