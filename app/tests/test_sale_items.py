import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.sale_item import SaleItem
from app.models.sale import Sale
from app.models.customer import Customer
from app.models.product import Product
from app.models import Base

# Use in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create the engine and session factory for tests
engine = create_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create all tables once per test session
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def session():
    # Create a new session for each test, rollback changes after test ends
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture
def dummy_customer(session):
    # Generate unique email to avoid UNIQUE constraint errors
    unique_email = f"test-{uuid.uuid4()}@example.com"
    customer = Customer(
        name="Test Customer",
        email=unique_email,
        phone="1234567890"
    )
    session.add(customer)
    session.commit()
    return customer

@pytest.fixture
def dummy_product(session):
    # Create a dummy product with a unique name or barcode to avoid conflicts if needed
    unique_name = f"Test Product {uuid.uuid4()}"
    product = Product(
        name=unique_name,
        brand="Test Brand",
        purchase_price=100,
        selling_price=150,
        stock=10,
        image=None,
        barcode=str(uuid.uuid4()),
        category="Test Category",
        unit="pcs"
    )
    session.add(product)
    session.commit()
    return product

@pytest.fixture
def dummy_sale(session, dummy_customer):
    sale = Sale(
        customer_id=dummy_customer.id,
        total_amount=1000  # some default total amount
    )
    session.add(sale)
    session.commit()
    return sale

def test_create_and_fetch_sale_item(session, dummy_sale, dummy_product):
    # Arrange
    test_item = SaleItem(
        sale_id=dummy_sale.id,
        product_id=dummy_product.id,
        name="Espresso",
        quantity=2,
        price_at_sale=300
    )
    session.add(test_item)
    session.commit()

    # Act
    fetched = session.query(SaleItem).filter_by(name="Espresso").first()

    # Assert
    assert fetched is not None
    assert fetched.name == "Espresso"
    assert fetched.quantity == 2
    assert fetched.price_at_sale == 300
    assert fetched.sale_id == dummy_sale.id
    assert fetched.product_id == dummy_product.id

def test_delete_sale_item(session, dummy_sale, dummy_product):
    item = SaleItem(
        sale_id=dummy_sale.id,
        product_id=dummy_product.id,
        name="Latte",
        quantity=1,
        price_at_sale=450
    )
    session.add(item)
    session.commit()

    session.delete(item)
    session.commit()

    fetched = session.query(SaleItem).filter_by(name="Latte").first()
    assert fetched is None
