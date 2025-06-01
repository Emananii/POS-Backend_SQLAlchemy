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
    """
    Helper to parse ISO date strings or return datetime objects as is.
    Raises SaleServiceError on invalid format or type.
    """
    if not input_date:
        return None
    if isinstance(input_date, str):
        try:
            # Parse ISO string into datetime (assuming no timezone info)
            parsed_date = datetime.fromisoformat(input_date)
            # Optionally convert naive datetime to UTC aware
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            return parsed_date
        except ValueError:
            raise SaleServiceError(f"Invalid date format: {input_date}")
    if isinstance(input_date, datetime):
        # Normalize naive datetime to UTC
        if input_date.tzinfo is None:
            return input_date.replace(tzinfo=timezone.utc)
        return input_date
    raise SaleServiceError(f"Invalid date type: {type(input_date)}")


def _validate_sale_items(sale_items_data):
    """
    Validates that sale_items_data is a non-empty list of dicts
    containing required keys with correct data types and values.
    """
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
    """
    Creates a Sale with associated SaleItems.
    Validates inputs, sets UTC timestamp, and commits transaction.
    Raises SaleServiceError on validation or DB errors.
    """
    # Verify customer exists
    customer = session.get(Customer, customer_id)
    if not customer:
        raise SaleServiceError(f"Customer with id {customer_id} does not exist")

    # Validate sale items data
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
        #deleted_at=None
    )

    try:
        session.add(new_sale)
        session.commit()
        return new_sale
    except IntegrityError as e:
        session.rollback()
        raise SaleServiceError(f"Failed to create sale: {e}")


def get_sale_by_id(session, sale_id, include_deleted=False):
    """
    Retrieves a sale by its ID.
    Excludes soft deleted sales unless include_deleted=True.
    """
    query = session.query(Sale).filter(Sale.id == sale_id)
    if not include_deleted:
        query = query.filter(Sale.deleted_at.is_(None))

    sale = query.one_or_none()
    if not sale:
        raise SaleServiceError(f"Sale with ID {sale_id} not found.")
    return sale


def get_sales_by_customer(session, customer_id, page=1, per_page=20):
    """
    Returns paginated list of sales for a customer, newest first.
    """
    if page < 1 or per_page < 1:
        raise SaleServiceError("page and per_page must be positive integers")

    query = (
        session.query(Sale)
        .filter(Sale.customer_id == customer_id, Sale.deleted_at.is_(None))
        .order_by(Sale.timestamp.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    return query.all()


def get_all_sales(session, page=1, per_page=20):
    """
    Returns paginated list of all sales, newest first.
    """
    if page < 1 or per_page < 1:
        raise SaleServiceError("page and per_page must be positive integers")

    query = (
        session.query(Sale)
        .filter(Sale.deleted_at.is_(None))
        .order_by(Sale.timestamp.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    return query.all()


def delete_sale(session, sale_id):
    """
    Soft deletes a sale by setting deleted_at timestamp.
    Commits the transaction.
    """
    try:
        sale = get_sale_by_id(session, sale_id)
        if sale.deleted_at is not None:
            raise SaleServiceError(f"Sale with ID {sale_id} is already deleted.")
        sale.deleted_at = datetime.now(timezone.utc)
        # Optionally update updated_at if you track it
        # sale.updated_at = datetime.now(timezone.utc)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise SaleServiceError(f"Failed to delete sale: {e}")


def get_sales_summary_by_day(session, start_date=None, end_date=None):
    """
    Returns daily sales totals, excluding soft deleted sales.
    Optional start_date and end_date can be ISO strings or datetimes.
    """
    start_date = _parse_date(start_date)
    end_date = _parse_date(end_date)

    query = session.query(
        func.date(Sale.timestamp).label("date"),
        func.sum(Sale.total_amount).label("total")
    ).filter(Sale.deleted_at.is_(None))

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
    """
    Returns total sales per customer, excluding soft deleted sales.
    Optional date filters accepted as ISO strings or datetimes.
    """
    start_date = _parse_date(start_date)
    end_date = _parse_date(end_date)

    query = session.query(
        Customer.id.label("customer_id"),
        Customer.name.label("customer_name"),
        func.sum(Sale.total_amount).label("total")
    ).join(Sale, Sale.customer_id == Customer.id).filter(Sale.deleted_at.is_(None))

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
