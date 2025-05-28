import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.sale_item import SaleItem
from app.models import Base

# Use in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create the engine and session factory for test
engine = create_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(bind=engine)

# Create all tables before running any test
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Fixture to create a clean session for each test
@pytest.fixture
def session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

# Test: Creating and fetching a SaleItem
def test_create_and_fetch_sale_item(session):
    # Arrange
    test_item = SaleItem(
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

# Optional: Test deletion too
def test_delete_sale_item(session):
    item = SaleItem(name="Latte", quantity=1, price_at_sale=450)
    session.add(item)
    session.commit()

    session.delete(item)
    session.commit()

    fetched = session.query(SaleItem).filter_by(name="Latte").first()
    assert fetched is None
