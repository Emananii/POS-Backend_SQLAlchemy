import pytest
from app.db.seed import seed_default_categories 
from app.db.engine import SessionLocal
from app.models.product import Product
from app.models.category import Category

def test_seed_categories():
    
    seed_default_categories()

    session = SessionLocal()

    
    categories = session.query(Category).all()
    
 
    assert len(categories) > 0, "Categories were not seeded properly!"

    
    session.query(Category).filter(Category.name.in_(['Beverages', 'Grocery', 'Snacks', 'Frozen Foods', 'Dairy'])).delete()
    session.commit()
    session.close()