from app.models.sale import Sale, Base
from app.models.customer import Customer
from app.db.engine import engine, SessionLocal
from datetime import datetime

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
    seed_sales()
