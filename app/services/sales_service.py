from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from ..db.engine import session as global_session
from ..models.sale import Sale
from ..models.sale_item import SaleItem
from ..models.customer import Customer


class SaleServiceError(Exception):
    """Custom exception for sale service errors."""
    pass


def _parse_date(input_date):
    if not input_date:
        return None
    if isinstance(input_date, str):
        try:
            parsed_date = datetime.fromisoformat(input_date)
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            return parsed_date
        except ValueError:
            raise SaleServiceError(f"Invalid date format: {input_date}")
    if isinstance(input_date, datetime):
        if input_date.tzinfo is None:
            return input_date.replace(tzinfo=timezone.utc)
        return input_date
    raise SaleServiceError(f"Invalid date type: {type(input_date)}")


def _validate_sale_items(sale_items_data):
    if not isinstance(sale_items_data, list) or len(sale_items_data) == 0:
        raise SaleServiceError("sale_items_data must be a non-empty list")

    for idx, item in enumerate(sale_items_data):
        required_keys = {"product_id", "name", "quantity", "price_at_sale"}
        if not isinstance(item, dict) or not required_keys.issubset(item.keys()):
            raise SaleServiceError(f"Missing required keys in sale_items_data at index {idx}")

        if not isinstance(item["product_id"], int) or item["product_id"] <= 0:
            raise SaleServiceError(f"Invalid product_id at index {idx}, must be positive integer")

        if not isinstance(item["name"], str) or not item["name"].strip():
            raise SaleServiceError(f"Invalid name at index {idx}, must be non-empty string")

        if not isinstance(item["quantity"], int) or item["quantity"] <= 0:
            raise SaleServiceError(f"Invalid quantity at index {idx}, must be positive integer")

        if not isinstance(item["price_at_sale"], (int, float)) or item["price_at_sale"] < 0:
            raise SaleServiceError(f"Invalid price_at_sale at index {idx}, must be non-negative number")


def create_sale(session, customer_id, sale_items_data):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise SaleServiceError(f"Customer with id {customer_id} does not exist")

    _validate_sale_items(sale_items_data)

    total = 0
    sale_items = []

    for item in sale_items_data:
        total += item["price_at_sale"] * item["quantity"]
        sale_items.append(SaleItem(
            product_id=item["product_id"],
            name=item["name"],
            quantity=item["quantity"],
            price_at_sale=item["price_at_sale"]
        ))

    new_sale = Sale(
        customer_id=customer_id,
        total_amount=total,
        items=sale_items,
        timestamp=datetime.now(timezone.utc),
    )

    try:
        session.add(new_sale)
        session.commit()
        return new_sale
    except IntegrityError as e:
        session.rollback()
        raise SaleServiceError(f"Failed to create sale: {e}")


def get_sale_by_id(session, sale_id):
    sale = session.query(Sale).filter(Sale.id == sale_id).one_or_none()
    if not sale:
        raise SaleServiceError(f"Sale with ID {sale_id} not found.")
    return sale


def get_sales_by_customer(session, customer_id, page=1, per_page=20):
    if page < 1 or per_page < 1:
        raise SaleServiceError("page and per_page must be positive integers")

    query = (
        session.query(Sale)
        .filter(Sale.customer_id == customer_id)
        .order_by(Sale.timestamp.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    return query.all()


def get_all_sales(session, page=1, per_page=20):
    if page < 1 or per_page < 1:
        raise SaleServiceError("page and per_page must be positive integers")

    query = (
        session.query(Sale)
        .order_by(Sale.timestamp.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    return query.all()

def get_recent_sales(session, limit=7):
    """
    Returns the most recent sales, including customer name and timestamp.
    """
    return (
        session.query(Sale)
        .join(Customer)
        .order_by(Sale.timestamp.desc())
        .limit(limit)
        .all()
    )


def delete_sale(session, sale_id):
    """
    Permanently deletes a sale.
    """
    try:
        sale = get_sale_by_id(session, sale_id)
        session.delete(sale)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise SaleServiceError(f"Failed to delete sale: {e}")


def get_sales_summary_by_day(session, start_date=None, end_date=None):
    start_date = _parse_date(start_date)
    end_date = _parse_date(end_date)

    query = session.query(
        func.date(Sale.timestamp).label("date"),
        func.sum(Sale.total_amount).label("total")
    )

    if start_date:
        query = query.filter(Sale.timestamp >= start_date)
    if end_date:
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


def get_sales_summary_by_customer(session, start_date=None, end_date=None):
    start_date = _parse_date(start_date)
    end_date = _parse_date(end_date)

    query = session.query(
        Customer.id.label("customer_id"),
        Customer.name.label("customer_name"),
        func.sum(Sale.total_amount).label("total")
    ).join(Sale, Sale.customer_id == Customer.id)

    if start_date:
        query = query.filter(Sale.timestamp >= start_date)
    if end_date:
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
