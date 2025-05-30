import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.models.product import Product
from app.models.category import Category  # Import Category

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)

def seed_default_category_for_test(session):
    category = session.query(Category).filter_by(name="Beverages").first()
    if not category:
        category = Category(name="Beverages", description="Drinks and refreshments")
        session.add(category)
        session.commit()
    return category

def seed_default_product_for_test(session):
    # Ensure category exists first
    category = seed_default_category_for_test(session)

    product = session.query(Product).filter_by(name="Coca-Cola").first()
    if not product:
        product = Product(
            name="Coca-Cola",
            brand="Coca-Cola",
            purchase_price=108,
            selling_price=120,
            stock=50,
            image="https://images.unsplash.com/photo-1622708862830-a026e3ef60bd?q=80&w=2564&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            barcode="5449000000996",
            category=category,  # Assign Category object here, not string
            unit="ml"
        )
        session.add(product)
        session.commit()

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def session():
    db = TestSessionLocal()
    seed_default_product_for_test(db)
    yield db
    db.rollback()
    db.close()

def test_add_product(session):
    product = session.query(Product).filter_by(name="Coca-Cola").first()
    assert product is not None
    assert product.name == "Coca-Cola"
    assert product.stock == 50

def test_update_product_stock(session):
    product = session.query(Product).filter_by(name="Coca-Cola").first()
    product.stock += 10
    session.commit()

    updated = session.query(Product).filter_by(name="Coca-Cola").first()
    assert updated.stock == 60

def test_product_exists_by_barcode(session):
    product = session.query(Product).filter_by(barcode="5449000000996").first()
    assert product is not None
    assert product.barcode == "5449000000996"
