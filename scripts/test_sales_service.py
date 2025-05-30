import pytest
import uuid
from app.services.sales_service import (
    create_sale, get_all_sales, get_sale_by_id, delete_sale, get_sales_summary_by_day
)
from app.db.engine import SessionLocal
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.product import Product
from app.models.customer import Customer

@pytest.fixture(scope="function")
def test_session():
    # Ensure a fresh DB session for each test
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="function")
def sample_customer(test_session):
    unique_email = f"test_{uuid.uuid4()}@example.com"  # unique email for each test run
    customer = Customer(name="Test Customer", email=unique_email)
    test_session.add(customer)
    test_session.commit()
    return customer

@pytest.fixture(scope="function")
def sample_products(test_session):
    products = [
        Product(name="Milk", brand="DairyCo", purchase_price=40, selling_price=50),
        Product(name="Eggs", brand="FarmFresh", purchase_price=20, selling_price=30)
    ]
    test_session.add_all(products)
    test_session.commit()
    return products

def test_create_sale(sample_customer, sample_products):
    # Use the product IDs from sample_products, but set custom price_at_sale to test logic
    sale_items_data = [
        {
            "product_id": sample_products[0].id,
            "name": sample_products[0].name,
            "quantity": 2,
            "price_at_sale": sample_products[0].selling_price
        },
        {
            "product_id": sample_products[1].id,
            "name": sample_products[1].name,
            "quantity": 1,
            "price_at_sale": sample_products[1].selling_price
        }
    ]

    sale = create_sale(sample_customer.id, sale_items_data)

    assert sale.id is not None
    assert len(sale.items) == 2

    expected_total = (
        sale_items_data[0]["quantity"] * sale_items_data[0]["price_at_sale"] +
        sale_items_data[1]["quantity"] * sale_items_data[1]["price_at_sale"]
    )
    assert sale.total_amount == expected_total

def test_get_all_sales_returns_sales():
    sales = get_all_sales()
    assert isinstance(sales, list)
    assert all(isinstance(s, Sale) for s in sales)

def test_get_sale_by_id(sample_customer, sample_products):
    sale = create_sale(sample_customer.id, [
        {"product_id": sample_products[0].id, "name": "Milk", "quantity": 1, "price_at_sale": 50}
    ])
    fetched = get_sale_by_id(sale.id)
    assert fetched.id == sale.id
    assert len(fetched.items) == 1

def test_delete_sale(sample_customer, sample_products):
    sale = create_sale(sample_customer.id, [
        {"product_id": sample_products[0].id, "name": "Milk", "quantity": 1, "price_at_sale": 50}
    ])
    result = delete_sale(sale.id)
    assert result is True

    with pytest.raises(ValueError):
        get_sale_by_id(sale.id)

def test_sales_summary_by_day(sample_customer, sample_products, test_session):
    from datetime import datetime

    sale = create_sale(sample_customer.id, [
        {"product_id": sample_products[0].id, "name": "Milk", "quantity": 1, "price_at_sale": 50}
    ])
    sale.created_at = datetime.utcnow()  # or appropriate datetime field
    test_session.commit()

    summary = get_sales_summary_by_day()
    print("Sales summary:", summary)

    assert isinstance(summary, list)
    assert len(summary) > 0
    # Fix here: access dict key 'total'
    assert any(isinstance(item['total'], (int, float)) and item['total'] > 0 for item in summary)
