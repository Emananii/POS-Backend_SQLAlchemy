from datetime import datetime
import random
from sqlalchemy import text
from app.db.engine import engine, SessionLocal
from app.models import Base
from app.models.customer import Customer
from app.models.product import Product
from app.models.category import Category
from app.models.sale import Sale
from app.models.sale_item import SaleItem

# Categories
CATEGORY_NAMES = ["Beverages", "Grocery", "Snacks", "Frozen Foods", "Dairy"]

# Sample data
CUSTOMERS = [
    {"name": "Walk-In", "email": "walkin@gmail.com"},
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Charlie", "email": "charlie@example.com"},
    {"name": "David", "email": "david@example.com"},
    {"name": "Eva", "email": "eva@example.com"},
    {"name": "Frank", "email": "frank@example.com"},
    {"name": "Grace", "email": "grace@example.com"},
    {"name": "Hannah", "email": "hannah@example.com"},
    {"name": "Isaac", "email": "isaac@example.com"},
]

PRODUCTS = [
    # Beverages
    {"name": "Coca-Cola", "brand": "Coca-Cola", "price": 120, "category": "Beverages"},
    {"name": "Pepsi", "brand": "PepsiCo", "price": 115, "category": "Beverages"},
    # Grocery
    {"name": "Maize Flour", "brand": "Unga", "price": 250, "category": "Grocery"},
    {"name": "Rice", "brand": "Sunrice", "price": 300, "category": "Grocery"},
    # Snacks
    {"name": "Potato Chips", "brand": "Lays", "price": 80, "category": "Snacks"},
    {"name": "Cookies", "brand": "Oreo", "price": 100, "category": "Snacks"},
    # Frozen Foods
    {"name": "Frozen Chicken", "brand": "FarmFresh", "price": 600, "category": "Frozen Foods"},
    {"name": "Fish Fingers", "brand": "SeaFresh", "price": 550, "category": "Frozen Foods"},
    # Dairy
    {"name": "Milk", "brand": "Brookside", "price": 60, "category": "Dairy"},
    {"name": "Cheese", "brand": "HappyCow", "price": 200, "category": "Dairy"},
]

def seed_categories(session):
    print("Seeding categories...")
    for name in CATEGORY_NAMES:
        if not session.query(Category).filter_by(name=name).first():
            session.add(Category(name=name))
    session.commit()

def seed_customers(session):
    print("Seeding customers...")
    for customer in CUSTOMERS:
        if not session.query(Customer).filter_by(email=customer["email"]).first():
            session.add(Customer(name=customer["name"], email=customer["email"]))
    session.commit()

def seed_products(session):
    print("Seeding products...")
    for p in PRODUCTS:
        category = session.query(Category).filter_by(name=p["category"]).first()
        if not category:
            continue

        if not session.query(Product).filter_by(name=p["name"]).first():
            product = Product(
                name=p["name"],
                brand=p["brand"],
                purchase_price=p["price"] - 10,
                selling_price=p["price"],
                stock=random.randint(30, 100),
                image="https://source.unsplash.com/300x300/?product",
                barcode=str(random.randint(1000000000000, 9999999999999)),
                category_id=category.id,
                unit="pcs"
            )
            session.add(product)
    session.commit()

def seed_sales_and_items(session, num_sales=10):
    print(f"Seeding {num_sales} sales with sale items...")
    customers = session.query(Customer).all()
    products = session.query(Product).all()

    for _ in range(num_sales):
        customer = random.choice(customers)
        selected_products = random.sample(products, k=random.randint(1, 3))

        total = sum(p.selling_price for p in selected_products)
        sale = Sale(customer_id=customer.id, total_amount=total)
        session.add(sale)
        session.flush()

        for product in selected_products:
            quantity = random.randint(1, 3)
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                name=product.name,
                quantity=quantity,
                price_at_sale=product.selling_price
            )
            session.add(sale_item)
    session.commit()

def show_tables():
    print("Current tables:")
    session = SessionLocal()
    tables = session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    for table in tables:
        print("-", table[0])
    session.close()

def run_seed():
    print("Creating all tables...")
    Base.metadata.create_all(engine)

    session = SessionLocal()
    seed_categories(session)
    seed_customers(session)
    seed_products(session)
    seed_sales_and_items(session, num_sales=15)
    show_tables()
    session.close()
    print("Seeding complete.")

if __name__ == "__main__":
    run_seed()