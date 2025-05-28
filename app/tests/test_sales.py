import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.models.customer import Customer
from app.models.sales import Sale


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
    
    test_customer = Customer(
        name="Sale Test User",
        email="saletestuser@gmail.com",
        phone="0700000000"
    )
    session.add(test_customer)
    session.commit()

   
    test_sale = Sale(
        customer_id=test_customer.id,
        timestamp=datetime.utcnow(),
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
    assert isinstance(fetched_sale.timestamp, datetime)


def test_sale_customer_relationship(session, seeded_customer_and_sale):
    _, test_sale = seeded_customer_and_sale
    related_customer = test_sale.customer  # Should be available via backref
    assert related_customer.name == "Sale Test User"
    assert related_customer.email == "saletestuser@gmail.com"
