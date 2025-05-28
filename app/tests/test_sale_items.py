from app.db.engine import engine, SessionLocal
from app.models.sale_item import SaleItem
from app.models import Base

# Register the model with metadata
Base.metadata.create_all(engine)

# Simulating a test sale item
session = SessionLocal()

test_item = SaleItem(
    #sale_id=1,
    #product_id=2,
    name="Espresso",
    quantity=2,
    price_at_sale=300
)

session.add(test_item)
session.commit()

# Fetch and print it
fetched = session.query(SaleItem).filter_by(name="Espresso").first()
print("Fetched from DB:", fetched)


session.delete(fetched)
session.commit()
session.close()
