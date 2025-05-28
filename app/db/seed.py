from app.models.customer import Customer
from app.models import Base
from app.db.engine import engine, SessionLocal
from app.models.product import Product
from sqlalchemy import text

def seed_default_customer():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(engine)

    session = SessionLocal()
    print("Checking if 'Walk-In' customer exists...")
    walk_in = session.query(Customer).filter_by(name="Walk-In").first()
    if not walk_in:
        print("Walk-In customer not found, adding it...")
        walk_in = Customer(id="1", name="Walk-In", email="walkin@gmail.com")
        session.add(walk_in)
        session.commit()
    else:
        print("Walk-in Customer already exists.")

    session.close()

if __name__ == "__main__":
    seed_default_customer()
    print("Seeding complete.")


def seed_default_product():
    print("Creating tables if they don't exist...")
    
    Base.metadata.create_all(engine)

    session = SessionLocal()
    
   
    product = session.query(Product).filter_by(name="Coca-Cola").first()
    if not product:
        print("Product Coca-Cola not found, adding it...")
        
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
    else:
        print("Product coca-cola already exists.")
    
    session.close()

def show_tables():
   
    print("Showing tables in the database:")
    session = SessionLocal()
    tables = session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    for table in tables:
        print(table[0])

    session.close()

if __name__ == "__main__":
    seed_default_product()
    show_tables()
    print("Seeding complete.")