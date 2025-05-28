import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.customer import Customer
from app.models import Base

# In-memory SQLite for isolated testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(bind=engine)

# Setup and teardown database schema for all tests
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Provide a clean session for each test
@pytest.fixture
def session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

# ✅ Test: Create, commit, fetch, and validate a customer
def test_create_and_fetch_customer(session):
    # Arrange
    test_customer = Customer(
        name="Test User",
        email="testuser@gmail.com",
        phone="0712345678"
    )
    session.add(test_customer)
    session.commit()

    # Act
    fetched = session.query(Customer).filter_by(email="testuser@gmail.com").first()

    # Assert
    assert fetched is not None
    assert fetched.name == "Test User"
    assert fetched.email == "testuser@gmail.com"
    assert fetched.phone == "0712345678"

# ✅ Optional test: deletion
def test_delete_customer(session):
    customer = Customer(
        name="Delete Me",
        email="deleteme@gmail.com",
        phone="0799999999"
    )
    session.add(customer)
    session.commit()

    # Delete it
    session.delete(customer)
    session.commit()

    # Ensure it's gone
    deleted = session.query(Customer).filter_by(email="deleteme@gmail.com").first()
    assert deleted is None
