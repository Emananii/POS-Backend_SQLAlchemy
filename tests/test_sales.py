from app.db.engine import SessionLocal, engine
from app.models.sale import Sale
from app.models.customer import Customer
from app.models import Base
from datetime import datetime

# Create tables (if not created)
Base.metadata.create_all(engine)

session = SessionLocal()

# Create a test customer
test_customer = Customer(
    name="Sale Test User",
    email="saletestuser@gmail.com",
    phone="0700000000"
)
session.add(test_customer)
session.commit()

# Create a test sale
test_sale = Sale(
    customer_id=test_customer.id,
    timestamp=datetime.utcnow(),
    total_amount=1500.0
)

session.add(test_sale)
session.commit()

# Fetch the sale
fetched_sale = session.query(Sale).filter_by(customer_id=test_customer.id).first()

if fetched_sale:
    print("Sale inserted and fetched successfully:")
    print(fetched_sale)
else:
    print("Failed to fetch sale.")

# Cleanup: delete test data
session.delete(fetched_sale)
session.delete(test_customer)
session.commit()

session.close()
