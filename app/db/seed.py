from models import Base
from models.customer import Customer
from db.engine import engine, SessionLocal


def seed_default_customer():
    Base.metadata.create_all(engine)

    session = SessionLocal()
    walk_in = session.query(Customer).filter_by(name="Walk-In").first()
    if not walk_in:
        walk_in = Customer(name="Walk-In", email="walkin@example.com")
        session.add(walk_in)
        session.commit()
    session.close()
