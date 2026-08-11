import pytest
from ingestion.pipeline import (
    load_sample_file,
    get_customers,
    get_products,
    get_orders,
    get_payments
)

def test_load_sample_files():
    customers = load_sample_file("customers.json")
    products = load_sample_file("products.json")
    orders = load_sample_file("orders.json")
    payments = load_sample_file("payments.json")

    assert len(customers) > 0
    assert len(products) > 0
    assert len(orders) > 0
    assert len(payments) > 0

def test_customer_resource_structure():
    customers = load_sample_file("customers.json")
    first = customers[0]
    assert "customer_id" in first
    assert "email" in first
    assert "status" in first

def test_failure_injection_duplicate_orders():
    normal_orders = load_sample_file("orders.json")
    injected_data = list(get_orders(inject_duplicate_orders=True))
    assert len(injected_data) == len(normal_orders) + 1

def test_failure_injection_null_customer():
    normal_customers = load_sample_file("customers.json")
    injected_data = list(get_customers(inject_null_customer=True))
    assert len(injected_data) == len(normal_customers) + 1
    assert injected_data[-1]["customer_id"] is None
