from datetime import datetime, timedelta, timezone

from app.db.engine import SessionLocal, Base, engine
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.services.reporting_service import (
    total_sales_per_customer,
    top_customers_by_sales,
    customer_purchase_frequency
)


def setup_test_data():
    session = SessionLocal()

    # Clear previous test data to keep environment clean
    session.query(SaleItem).delete()
    session.query(Sale).delete()
    session.query(Customer).delete()
    session.commit()

    # Create customers
    cust1 = Customer(name="Alice", email="alice@example.com")
    cust2 = Customer(name="Bob", email="bob@example.com")
    cust3 = Customer(name="Charlie", email="charlie@example.com")

    session.add_all([cust1, cust2, cust3])
    session.commit()

    # Create sales with different dates and customers
    now = datetime.now(timezone.utc)
    sales = [
        Sale(customer_id=cust1.id, timestamp=now -
             timedelta(days=5), total_amount=150),
        Sale(customer_id=cust1.id, timestamp=now -
             timedelta(days=2), total_amount=200),
        Sale(customer_id=cust2.id, timestamp=now -
             timedelta(days=1), total_amount=300),
        Sale(customer_id=cust3.id, timestamp=now, total_amount=100),
    ]

    session.add_all(sales)
    session.commit()

    session.close()


def quick_test():
    setup_test_data()

    print("\n--- Total Sales Per Customer ---")
    results = total_sales_per_customer()
    for r in results:
        print(r)

    print("\n--- Top Customers By Sales (limit=2) ---")
    top_results = top_customers_by_sales(limit=2)
    for r in top_results:
        print(r)

    print("\n--- Customer Purchase Frequency ---")
    freq_results = customer_purchase_frequency()
    for r in freq_results:
        print(r)


if __name__ == "__main__":
    quick_test()
