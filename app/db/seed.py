from datetime import datetime
from sqlalchemy import text
from app.db.engine import engine, SessionLocal
from app.models import Base
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale

def seed_default_customer():
    session = SessionLocal()
    walk_in = session.query(Customer).filter_by(name="Walk-In").first()
    if not walk_in:
        print("Adding Walk-In customer...")
        walk_in = Customer(id="1", name="Walk-In", email="walkin@gmail.com")
        session.add(walk_in)
        session.commit()
    else:
        print("Walk-in Customer already exists.")
    session.close()

def seed_default_product():
    session = SessionLocal()
    product = session.query(Product).filter_by(name="Coca-Cola").first()
    if not product:
        print("Adding Coca-Cola product...")
        product = Product(
            name="Coca-Cola",
            brand="Coca-Cola",
            purchase_price=108,
            selling_price=120,
            stock=50,
            image="https://images.unsplash.com/photo-1622708862830-a026e3ef60bd?q=80&w=2564&auto=format&fit=crop",
            barcode="5449000000996",
            category="Beverages",
            unit="ml"
        )
        session.add(product)
        session.commit()
    else:
        print("Coca-Cola product already exists.")
    session.close()

def seed_sales():
    session = SessionLocal()
    walk_in = session.query(Customer).filter_by(name="Walk-In").first()
    if walk_in:
        print("Seeding a sample sale...")
        sample_sale = Sale(customer_id=walk_in.id, total_amount=500.00, timestamp=datetime.utcnow())
        session.add(sample_sale)
        session.commit()
    else:
        print("Walk-In customer not found. Seed that first.")
    session.close()

def show_tables():
    print("Tables in DB:")
    session = SessionLocal()
    tables = session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    for table in tables:
        print(f"- {table[0]}")
    session.close()

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    seed_default_customer()
    seed_default_product()
    seed_sales()
    show_tables()
    print("Seeding complete.")
