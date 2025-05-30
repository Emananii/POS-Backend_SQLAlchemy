from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from ..db.engine import session
from ..models.sale import Sale
from ..models.sale_item import SaleItem
from sqlalchemy import func

# CREATE
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

    # Use timezone-aware UTC datetime here
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

# READ
def get_sale_by_id(sale_id):
    # Use session.get() for primary key lookup (new recommended approach)
    sale = session.get(Sale, sale_id)
    if not sale:
        raise ValueError(f"Sale with ID {sale_id} not found.")
    return sale

def get_sales_by_customer(customer_id):
    return session.query(Sale).filter(Sale.customer_id == customer_id).order_by(Sale.timestamp.desc()).all()

def get_all_sales():
    return session.query(Sale).order_by(Sale.timestamp.desc()).all()

# DELETE
def delete_sale(sale_id):
    sale = get_sale_by_id(sale_id)
    session.delete(sale)
    session.commit()
    return True

# [Optional] Daily summary (total revenue per day)
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

    # Normalize date format to string ISO
    return [
        {
            "date": row.date.isoformat() if hasattr(row.date, "isoformat") else str(row.date),
            "total": row.total
        }
        for row in results
    ]
