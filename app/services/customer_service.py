from sqlalchemy.exc import IntegrityError
from app.models.customer import Customer
from app.models.sale import Sale
from app.db.engine import SessionLocal

# CREATE
def create_customer(name, email, phone=None, customer_type="individual", company_name=None, discount_rate=0):
    customer = Customer(
        name=name,
        email=email,
        phone=phone,
        customer_type=customer_type,
        company_name=company_name,
        discount_rate=discount_rate
    )
    with SessionLocal() as session:
        try:
            session.add(customer)
            session.commit()
            session.refresh(customer)
            return customer
        except IntegrityError:
            session.rollback()
            raise ValueError("A customer with this email already exists.")


# READ
def get_customer_by_id(customer_id):
    with SessionLocal() as session:
        customer = session.query(Customer).get(customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        return customer


def get_customer_by_email(email):
    with SessionLocal() as session:
        customer = session.query(Customer).filter_by(email=email).first()
        if not customer:
            raise ValueError(f"Customer with email '{email}' not found.")
        return customer


def get_all_customers():
    with SessionLocal() as session:
        return session.query(Customer).order_by(Customer.name).all()


def get_purchases_by_customer(customer_id: int):
    """
    Fetch all sales made by a given customer including their sale items.
    Returns None if customer doesn't exist.
    """
    with SessionLocal() as session:
        customer = session.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None

        sales = session.query(Sale).filter(Sale.customer_id == customer_id).all()
        return sales


# UPDATE
def update_customer(customer_id, **kwargs):
    with SessionLocal() as session:
        customer = session.query(Customer).get(customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")

        for key, value in kwargs.items():
            if hasattr(customer, key):
                setattr(customer, key, value)

        session.commit()
        session.refresh(customer)
        return customer


# DELETE
def delete_customer(customer_id):
    with SessionLocal() as session:
        customer = session.query(Customer).get(customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")

        session.delete(customer)
        session.commit()
        return True


# BUSINESS LOGIC
def add_loyalty_points(customer_id, points):
    with SessionLocal() as session:
        customer = session.query(Customer).get(customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        customer.loyalty_points += points
        session.commit()
        session.refresh(customer)
        return customer


def apply_discount(customer_id, discount_percentage):
    with SessionLocal() as session:
        customer = session.query(Customer).get(customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        customer.discount_rate = discount_percentage
        session.commit()
        session.refresh(customer)
        return customer