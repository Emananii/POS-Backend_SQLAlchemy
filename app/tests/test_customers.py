from app.db.engine import SessionLocal, engine
from app.models.customer import Customer
from app.models import Base

Base.metadata.create_all(engine)

session = SessionLocal()

test_customer = Customer(
    name="Test User",
    email="testuser@gmail.com",
    phone="0712345678"
)


session.add(test_customer)
session.commit()

fetched = session.query(Customer).filter_by(email="testuser@gmail.com").first()

if fetched:
    print("Customer inserted and fetched successfully:")
    print(fetched)
else:
    print("Failed to fetch customer")

if fetched:
    session.delete(fetched)
    session.commit()

session.close()
