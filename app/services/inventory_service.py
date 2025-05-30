from app.models.product import Product
from app.models.category import Category
from app.db.engine import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_product(db, name, brand, purchase_price, selling_price, stock, image, barcode, category_id, unit):

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise ValueError("Category not found")
    
    
    new_product = Product(
        name=name,
        brand=brand,
        purchase_price=purchase_price,
        selling_price=selling_price,
        stock=stock,
        image=image,
        barcode=barcode,
        category_id=category_id,
        unit=unit
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def update_product(db, product_id, name=None, brand=None, purchase_price=None, selling_price=None, stock=None, image=None, barcode=None, category_id=None, unit=None):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError("Product not found")
    
    if name:
        product.name = name
    if brand:
        product.brand = brand
    if purchase_price:
        product.purchase_price = purchase_price
    if selling_price:
        product.selling_price = selling_price
    if stock is not None:
        product.stock = stock
    if image:
        product.image = image
    if barcode:
        product.barcode = barcode
    if category_id:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise ValueError("Category not found")
        product.category_id = category_id
    if unit:
        product.unit = unit

    db.commit()
    db.refresh(product)
    return product


def get_product_by_id(db, product_id):
    return db.query(Product).filter(Product.id == product_id).first()

def get_all_products(db):
    return db.query(Product).all()

def get_products_by_category(db, category_id):
    return db.query(Product).filter(Product.category_id == category_id).all()


def search_products_by_name(db, name):
    return db.query(Product).filter(Product.name.ilike(f"%{name}%")).all()


def get_products_in_stock(db):
    return db.query(Product).filter(Product.stock > 0).all()


def get_category_by_id(db, category_id):
    return db.query(Category).filter(Category.id == category_id).first()


def create_category(db, name, description=None):
    new_category = Category(name=name, description=description)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


def update_category(db, category_id, name=None, description=None):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise ValueError("Category not found")
    
    if name:
        category.name = name
    if description:
        category.description = description
    
    db.commit()
    db.refresh(category)
    return category
