import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.models.product import Product

# ✅ Use in-memory SQLite test DB
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)

# ✅ Seeding logic for test DB — same logic as in seed.py, but here
def seed_default_product_for_test(session):
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
            category="Beverages",
            unit="ml"
        )
        session.add(product)
        session.commit()

# ✅ Setup schema once per session
@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

# ✅ Provide seeded session for each test
@pytest.fixture
def session():
    db = TestSessionLocal()
    seed_default_product_for_test(db)
    yield db
    db.rollback()
    db.close()

# ✅ Test 1: Ensure product is seeded
def test_add_product(session):
    product = session.query(Product).filter_by(name="Coca-Cola").first()
    assert product is not None
    assert product.name == "Coca-Cola"
    assert product.stock == 50  # Confirm seed worked

# ✅ Test 2: Modify and check stock
def test_update_product_stock(session):
    product = session.query(Product).filter_by(name="Coca-Cola").first()
    product.stock += 10
    session.commit()

    updated = session.query(Product).filter_by(name="Coca-Cola").first()
    assert updated.stock == 60

# ✅ Test 3: Confirm barcode exists
def test_product_exists_by_barcode(session):
    product = session.query(Product).filter_by(barcode="5449000000996").first()
    assert product is not None
    assert product.barcode == "5449000000996"