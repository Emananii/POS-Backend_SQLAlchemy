from app.models.customer import Customer
from app.models import Base
from app.models.sale_item import SaleItem
from app.db.engine import engine, SessionLocal

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
    session.close()

def seed_sale_items():
    print("Seeding SaleItem records...")
    session = SessionLocal()

    
    existing = session.query(SaleItem).filter_by(name="Espresso").first()
    if existing:
        print("Sample sale items already seeded.")
        session.close()
        return

    items = [
        SaleItem(sale_id=1, product_id=1, name="Espresso", quantity=2, price_at_sale=300),
        SaleItem(sale_id=1, product_id=2, name="Latte", quantity=1, price_at_sale=450),
        SaleItem(sale_id=2, product_id=3, name="Cappuccino", quantity=3, price_at_sale=400),
    ]

    session.add_all(items)
    session.commit()
    session.close()
    print("Sale items seeded successfully.")

def seed_sales():
    Base.metadata.create_all(engine)

    session = SessionLocal()

    walk_in = session.query(Customer).filter_by(name="Walk-In").first()
    if walk_in:
        sample_sale = Sale(customer_id=walk_in.id, total_amount=500.00, timestamp=datetime.utcnow())
        session.add(sample_sale)
        session.commit()
        print("Sale added for Walk-In customer.")
    else:
        print("Walk-In customer not found. Seed that first.")

    session.close()

if __name__ == "__main__":
    seed_default_customer()
    seed_sale_items()
    print("All seeding complete.")