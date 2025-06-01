from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from ..db.engine import session
from ..models.sale import Sale
from ..models.sale_item import SaleItem
from sqlalchemy import func


def create_sale(customer_id, sale_items_data):
    """
    Creates a Sale with associated SaleItems.
    Explicitly sets the timestamp to current UTC datetime to ensure
    it's available for queries that rely on timestamp.
    """

    total = 0
    sale_items = []

    for item in sale_items_data:
        total += item["price_at_sale"] * item["quantity"]
        sale_item = SaleItem(
            product_id=item["product_id"],
            name=item["name"],
            quantity=item["quantity"],
            price_at_sale=item["price_at_sale"]
        )
        sale_items.append(sale_item)

    
    new_sale = Sale(
        customer_id=customer_id,
        total_amount=total,
        items=sale_items,
        timestamp=datetime.now(timezone.utc)  # Fixed: timezone aware UTC datetime
    )

    try:
        session.add(new_sale)
        session.commit()
        return new_sale
    except IntegrityError as e:
        session.rollback()
        raise ValueError(f"Failed to create sale: {e}")


def get_sale_by_id(sale_id):
    
    sale = session.get(Sale, sale_id)
    if not sale:
        raise ValueError(f"Sale with ID {sale_id} not found.")
    return sale

def get_sales_by_customer(customer_id):
    return session.query(Sale).filter(Sale.customer_id == customer_id).order_by(Sale.timestamp.desc()).all()

def get_all_sales():
    return session.query(Sale).order_by(Sale.timestamp.desc()).all()


def delete_sale(sale_id):
    sale = get_sale_by_id(sale_id)
    session.delete(sale)
    session.commit()
    return True

def get_sales_summary_by_day(start_date=None, end_date=None):
    """
    Returns a list of daily sales summaries.
    Each item contains {"date": "YYYY-MM-DD", "total": float}
    Optionally filter by start_date and/or end_date (ISO string or datetime).
    """

    query = session.query(
        func.date(Sale.timestamp).label("date"),
        func.sum(Sale.total_amount).label("total")
    )

    if start_date:
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        query = query.filter(Sale.timestamp >= start_date)

    if end_date:
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        query = query.filter(Sale.timestamp <= end_date)

    query = query.group_by(func.date(Sale.timestamp)).order_by(func.date(Sale.timestamp).desc())

    results = query.all()

    return [
        {
            "date": row.date.isoformat() if hasattr(row.date, "isoformat") else str(row.date),
            "total": row.total
        }
        for row in results
    ]
    
def get_sales_summary_by_customer(start_date=None, end_date=None):
    """
    Returns a summary of total sales per customer.
    Optionally filter by date range.
    Each item contains {"customer_id": int, "customer_name": str, "total": float}
    """

    from ..models.customer import Customer

    query = session.query(
        Customer.id.label("customer_id"),
        Customer.name.label("customer_name"),
        func.sum(Sale.total_amount).label("total")
    ).join(Sale, Sale.customer_id == Customer.id)

    if start_date:
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        query = query.filter(Sale.timestamp >= start_date)

    if end_date:
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        query = query.filter(Sale.timestamp <= end_date)

    query = query.group_by(Customer.id, Customer.name).order_by(func.sum(Sale.total_amount).desc())

    results = query.all()

    return [
        {
            "customer_id": row.customer_id,
            "customer_name": row.customer_name,
            "total_sales": row.total
        }
        for row in results
    ]