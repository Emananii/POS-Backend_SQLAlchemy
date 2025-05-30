import pytest
from sqlalchemy.exc import IntegrityError
from app.services.customer_service import (
    create_customer, get_all_customers, get_customer_by_id,
    update_customer, delete_customer, add_loyalty_points, apply_discount,
    get_purchases_by_customer
)
from app.services.sales_service import create_sale
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale_item import SaleItem
from app.models.sale import Sale
from app.db.engine import SessionLocal, Base, engine

# --- Fixtures ---


@pytest.fixture(autouse=True, scope="function")
def reset_db():
    """
    Automatically runs before each test. Drops and recreates all tables to ensure test isolation.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Optional post-test cleanup


@pytest.fixture(scope="function")
def test_session():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def sample_products(test_session):
    product1 = Product(
        name="Bread",
        brand="Generic",
        purchase_price=10.0,
        selling_price=20.0,
        stock=100
    )
    product2 = Product(
        name="Butter",
        brand="Generic",
        purchase_price=8.0,
        selling_price=15.0,
        stock=50
    )
    test_session.add_all([product1, product2])
    test_session.commit()
    return [product1, product2]


# --- Tests ---


def test_create_customers():
    c1 = create_customer(
        "Alice Wanjiku", "alice1@example.com", phone="0711222333")
    c2 = create_customer(
        "Bob Oduor", "bob1@example.com",
        customer_type="business", company_name="Oduor Ltd", discount_rate=10
    )

    assert c1.id is not None
    assert c2.customer_type == "business"
    assert c2.company_name == "Oduor Ltd"
    assert c2.discount_rate == 10


def test_create_duplicate_email_raises_integrity_error():
    create_customer("Test", "dup@example.com")
    # <- Your create_customer raises ValueError, not IntegrityError
    with pytest.raises(ValueError):
        create_customer("Duplicate", "dup@example.com")


def test_get_all_customers():
    create_customer("One", "one1@example.com")
    create_customer("Two", "two1@example.com")
    customers = get_all_customers()
    assert isinstance(customers, list)
    assert len(customers) == 2


def test_get_customer_by_id():
    customer = create_customer("Single", "single1@example.com")
    fetched = get_customer_by_id(customer.id)
    assert fetched.email == "single1@example.com"


def test_update_customer():
    customer = create_customer("Updatable", "update1@example.com")
    updated = update_customer(
        customer.id, name="Updated Name", phone="0799999999")
    assert updated.name == "Updated Name"
    assert updated.phone == "0799999999"


def test_add_loyalty_points():
    customer = create_customer("Loyal", "loyal1@example.com")
    add_loyalty_points(customer.id, 50)
    updated = get_customer_by_id(customer.id)
    assert updated.loyalty_points == 50


def test_apply_discount():
    customer = create_customer(
        "Discounted", "discount1@example.com", customer_type="business")
    apply_discount(customer.id, 20)
    updated = get_customer_by_id(customer.id)
    assert updated.discount_rate == 20


def test_delete_customer():
    customer = create_customer("Deletable", "delete1@example.com")
    delete_customer(customer.id)
    with pytest.raises(ValueError):
        get_customer_by_id(customer.id)


def test_get_purchases_by_customer(sample_products):
    customer = create_customer(
        name="Jane Doe", email="jane1@example.com", phone="1234567890")
    sale = create_sale(customer.id, [
        {"product_id": sample_products[0].id, "name": "Bread",
            "quantity": 1, "price_at_sale": 20},
        {"product_id": sample_products[1].id,
            "name": "Butter", "quantity": 2, "price_at_sale": 15}
    ])

    purchases = get_purchases_by_customer(customer.id)
    assert purchases is not None
    assert len(purchases) == 1
    assert purchases[0].total_amount == 50  # 1*20 + 2*15
    assert len(purchases[0].items) == 2
