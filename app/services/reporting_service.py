from sqlalchemy import func
from app.db.engine import SessionLocal
from app.models.customer import Customer
from app.models.sale import Sale

def total_sales_per_customer(start_date=None, end_date=None):
    session = SessionLocal()
    query = session.query(
        Customer.id,
        Customer.name,
        func.coalesce(func.sum(Sale.total_amount), 0).label("total_sales")
    ).join(Sale, Sale.customer_id == Customer.id, isouter=True)

    if start_date:
        query = query.filter(Sale.timestamp >= start_date)
    if end_date:
        query = query.filter(Sale.timestamp <= end_date)

    query = query.group_by(Customer.id, Customer.name).order_by(Customer.name)

    results = query.all()
    session.close()
    return [{"customer_id": r.id, "customer_name": r.name, "total_sales": r.total_sales} for r in results]

def top_customers_by_sales(limit=5, start_date=None, end_date=None):
    session = SessionLocal()
    query = session.query(
        Customer.id,
        Customer.name,
        func.coalesce(func.sum(Sale.total_amount), 0).label("total_sales")
    ).join(Sale, Sale.customer_id == Customer.id)

    if start_date:
        query = query.filter(Sale.timestamp >= start_date)
    if end_date:
        query = query.filter(Sale.timestamp <= end_date)

    query = query.group_by(Customer.id, Customer.name)
    query = query.order_by(func.sum(Sale.total_amount).desc())
    query = query.limit(limit)

    results = query.all()
    session.close()
    return [{"customer_id": r.id, "customer_name": r.name, "total_sales": r.total_sales} for r in results]

def customer_purchase_frequency(start_date=None, end_date=None):
    session = SessionLocal()
    query = session.query(
        Customer.id,
        Customer.name,
        func.count(Sale.id).label("purchase_count")
    ).join(Sale, Sale.customer_id == Customer.id)

    if start_date:
        query = query.filter(Sale.timestamp >= start_date)
    if end_date:
        query = query.filter(Sale.timestamp <= end_date)

    query = query.group_by(Customer.id, Customer.name)
    query = query.order_by(func.count(Sale.id).desc())

    results = query.all()
    session.close()
    return [{"customer_id": r.id, "customer_name": r.name, "purchase_count": r.purchase_count} for r in results]

