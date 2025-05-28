from app.models.customer import Customer, Base
from app.db.engine import engine, SessionLocal

def seed_default_customer():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(engine)

    session = SessionLocal()
    print("Checking if 'Walk-In' customer exists...")
    walk_in = session.query(Customer).filter_by(name="Walk-In").first()
    if not walk_in:
        print("Walk-In customer not found, adding it...")
        walk_in = Customer(id = "1",name="Walk-In", email="walkin@gmail.com")
        session.add(walk_in)
        session.commit()
    session.close()

if __name__ == "__main__":
    seed_default_customer()
    print("Seeding complete.")
    
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