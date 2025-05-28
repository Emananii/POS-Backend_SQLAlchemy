import pytest
from models import Base, Product, Customer
from sales import Cart
from database import Session as DBSession
import os

@pytest.fixture(autouse=True)
def clean_db():
    # Only for testing – clear tables before each test
    session = DBSession()
    session.query(Product).delete()
    session.query(Customer).delete()
    session.commit()
    yield
    session.close()

@pytest.fixture
def session():
    return DBSession()

@pytest.fixture
def sample_product(session):
    product = Product(name="Test Product", price=100, stock=10)
    session.add(product)
    session.commit()
    return product

def test_cart_add_and_total(sample_product):
    cart = Cart()
    cart.add_item(sample_product, 2)
    assert cart.total_price() == 200

def test_checkout_updates_stock_and_customer(sample_product):
    cart = Cart()
    cart.add_item(sample_product, 3)

    customer_info = {
        'name': 'Alice',
        'email': 'alice@example.com',
        'phone': '0700111222'
    }
    sale = cart.checkout(customer_email='alice@example.com', customer_info=customer_info)

    session = DBSession()
    updated = session.query(Product).filter_by(name="Test Product").first()
    customer = session.query(Customer).filter_by(email="alice@example.com").first()
    assert updated.stock == 7
    assert customer.name == 'Alice'
    session.close()
