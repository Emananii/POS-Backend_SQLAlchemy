import pytest
from datetime import datetime, UTC
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.models.customer import Customer
from app.models.sale import Sale

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def session():
    db = TestSessionLocal()
    yield db
    db.rollback()
    db.close()


@pytest.fixture
def seeded_customer_and_sale(session):
    unique_email = f"saletestuser_{uuid4().hex[:6]}@gmail.com"
    test_customer = Customer(
        name="Sale Test User",
        email=unique_email,
        phone="0700000000"
    )
    session.add(test_customer)
    session.commit()

    test_sale = Sale(
        customer_id=test_customer.id,
        timestamp=datetime.now(UTC),
        total_amount=1500.0
    )
    session.add(test_sale)
    session.commit()

    return test_customer, test_sale


def test_sale_creation_and_fetch(session, seeded_customer_and_sale):
    test_customer, test_sale = seeded_customer_and_sale

    fetched_sale = session.query(Sale).filter_by(customer_id=test_customer.id).first()
    assert fetched_sale is not None
    assert fetched_sale.total_amount == 1500.0
    assert fetched_sale.customer_id == test_customer.id


def test_sale_customer_relationship(session, seeded_customer_and_sale):
    test_customer, test_sale = seeded_customer_and_sale

    fetched_sale = session.query(Sale).filter_by(id=test_sale.id).first()
    assert fetched_sale.customer.name == "Sale Test User"
