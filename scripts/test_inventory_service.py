import pytest
from app.db.engine import SessionLocal
from app.models.product import Product
from app.models.category import Category
from app.services.inventory_service import (
    create_product,
    update_product,
    get_product_by_id,
    get_all_products,
    get_products_by_category,
    search_products_by_name,
    get_products_in_stock,
    create_category,
    update_category,
    get_category_by_id,
)
import uuid

@pytest.fixture(scope="function")
def db_session():
    """Create a new database session for testing."""
    db = SessionLocal()
  
    db.query(Product).delete()
    db.query(Category).delete()
    db.commit()
    try:
        yield db
    finally:
        db.rollback()  
        db.close()


def generate_unique_category_name():
    return f"Category-{uuid.uuid4()}"


@pytest.fixture
def create_sample_category(db_session):
    """Create a sample category for testing purposes."""
    category_name = generate_unique_category_name()
    category = Category(name=category_name, description="Electronic goods")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def create_sample_product(db_session, create_sample_category):
    """Create a sample product linked to a category for testing."""
    product = Product(
        name="Smartphone",
        brand="BrandX",
        purchase_price=200.0,
        selling_price=300.0,
        stock=50,
        image="smartphone.jpg",
        barcode="123456789",
        category_id=create_sample_category.id,
        unit="Piece"
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def test_create_product(db_session, create_sample_category):
    product = create_product(
        db_session,
        name="Laptop",
        brand="BrandY",
        purchase_price=500.0,
        selling_price=700.0,
        stock=30,
        image="laptop.jpg",
        barcode="987654321",
        category_id=create_sample_category.id,
        unit="Piece"
    )
    assert product.name == "Laptop"
    assert product.stock == 30
    assert product.category_id == create_sample_category.id


def test_update_product(db_session, create_sample_product):
    updated_product = update_product(
        db_session,
        product_id=create_sample_product.id,
        name="Smartphone Pro",
        stock=60
    )
    assert updated_product.name == "Smartphone Pro"
    assert updated_product.stock == 60

def test_get_product_by_id(db_session, create_sample_product):
    product = get_product_by_id(db_session, create_sample_product.id)
    assert product.name == "Smartphone"
    assert product.stock == 50

def test_get_all_products(db_session, create_sample_product):
    products = get_all_products(db_session)
    assert len(products) > 0

9
def test_get_products_by_category(db_session, create_sample_category, create_sample_product):
    products = get_products_by_category(db_session, create_sample_category.id)
    assert len(products) > 0
    assert products[0].category_id == create_sample_category.id

def test_search_products_by_name(db_session, create_sample_product):
    products = search_products_by_name(db_session, "Smartphone")
    assert len(products) > 0
    assert products[0].name == "Smartphone"


def test_get_products_in_stock(db_session, create_sample_product):
    products = get_products_in_stock(db_session)
    assert len(products) > 0
    assert products[0].stock > 0


def test_create_category(db_session):
    category_name = generate_unique_category_name()
    category = create_category(db_session, name=category_name, description="Home furniture")
    assert category.name == category_name
    assert category.description == "Home furniture"

def test_update_category(db_session, create_sample_category):
    updated_category = update_category(
        db_session, category_id=create_sample_category.id, name="Home Electronics"
    )
    assert updated_category.name == "Home Electronics"

def test_get_category_by_id(db_session, create_sample_category):
    category = get_category_by_id(db_session, create_sample_category.id)
    assert category.name == create_sample_category.name
    assert category.description == create_sample_category.description
