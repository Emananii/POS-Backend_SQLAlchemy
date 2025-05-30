# tests/test_reporting_service.py

import pytest
from datetime import datetime, timedelta, timezone

from app.db.engine import SessionLocal
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.services.reporting_service import (
    total_sales_per_customer,
    top_customers_by_sales,
    customer_purchase_frequency
)


@pytest.fixture(scope="function")
def setup_test_data():
    session = SessionLocal()

    # Clear previous test data
    session.query(SaleItem).delete()
    session.query(Sale).delete()
    session.query(Customer).delete()
    session.commit()

    # Create customers
    cust1 = Customer(name="Alice", email="alice@example.com")
    cust2 = Customer(name="Bob", email="bob@example.com")
    cust3 = Customer(name="Charlie", email="charlie@example.com")

    session.add_all([cust1, cust2, cust3])
    session.commit()

    # Create sales with different dates and customers
    now = datetime.now(timezone.utc)
    sales = [
        Sale(customer_id=cust1.id, timestamp=now - timedelta(days=5), total_amount=150),
        Sale(customer_id=cust1.id, timestamp=now - timedelta(days=2), total_amount=200),
        Sale(customer_id=cust2.id, timestamp=now - timedelta(days=1), total_amount=300),
        Sale(customer_id=cust3.id, timestamp=now, total_amount=100),
    ]

    session.add_all(sales)
    session.commit()
    session.close()


def test_total_sales_per_customer(setup_test_data):
    results = total_sales_per_customer()

    assert len(results) == 3

    # Expect customer_id 1 (Alice) to have total of 350
    alice_result = next((r for r in results if r["customer_name"] == "Alice"), None)
    assert alice_result is not None
    assert alice_result["total_sales"] == 350

    # Expect Bob to have 300, Charlie to have 100
    bob_result = next((r for r in results if r["customer_name"] == "Bob"), None)
    charlie_result = next((r for r in results if r["customer_name"] == "Charlie"), None)

    assert bob_result["total_sales"] == 300
    assert charlie_result["total_sales"] == 100


def test_top_customers_by_sales(setup_test_data):
    top_customers = top_customers_by_sales(limit=2)

    assert len(top_customers) == 2
    assert top_customers[0]["customer_name"] in {"Alice", "Bob"}
    assert top_customers[1]["customer_name"] in {"Alice", "Bob"}
    assert top_customers[0]["total_sales"] >= top_customers[1]["total_sales"]

    # Alice and Bob should be in the top two
    customer_names = {c["customer_name"] for c in top_customers}
    assert "Alice" in customer_names
    assert "Bob" in customer_names


def test_customer_purchase_frequency(setup_test_data):
    frequencies = customer_purchase_frequency()

    assert len(frequencies) == 3

    alice_freq = next((f for f in frequencies if f["customer_name"] == "Alice"), None)
    assert alice_freq is not None
    assert alice_freq["purchase_count"] == 2

    bob_freq = next((f for f in frequencies if f["customer_name"] == "Bob"), None)
    charlie_freq = next((f for f in frequencies if f["customer_name"] == "Charlie"), None)

    assert bob_freq["purchase_count"] == 1
    assert charlie_freq["purchase_count"] == 1
