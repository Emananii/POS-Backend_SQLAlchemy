
import pytest
from app.db.seed import seed_default_product
from app.db.engine import SessionLocal
from app.models.product import Product


@pytest.fixture(scope="module")
def setup_database():
 
    seed_default_product()   
    yield
   

def test_add_product(setup_database):
    session = SessionLocal()

    
    product = session.query(Product).filter_by(name="Coca-Cola").first()
    
    assert product is not None
    assert product.name == "Coca-Cola"
    assert product.stock == 50

    session.close()


def test_update_product_stock(setup_database):
    session = SessionLocal()

   
    product = session.query(Product).filter_by(name="Coca-Cola").first()
    
   
    product.stock += 10 
    session.commit()

    
    updated_product = session.query(Product).filter_by(name="Coca-Cola").first()
    assert updated_product.stock == 60  

    session.close()


def test_product_exists_by_barcode(setup_database):
    session = SessionLocal()

    
    product = session.query(Product).filter_by(barcode="5449000000996").first()
    
    
    assert product is not None
    assert product.barcode == "5449000000996"

    session.close()
