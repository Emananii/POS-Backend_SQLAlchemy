
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from ..models.customer import Customer
from ..db.engine import session

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
    try:
        session.add(customer)
        session.commit()
        return customer
    except IntegrityError:
        session.rollback()
        raise ValueError("A customer with this email already exists.")


# READ

def get_customer_by_id(customer_id):
    customer = session.query(Customer).get(customer_id)
    if not customer:
        raise ValueError(f"Customer with ID {customer_id} not found.")
    return customer

def get_customer_by_email(email):
    customer = session.query(Customer).filter_by(email=email).first()
    if not customer:
        raise ValueError(f"Customer with email '{email}' not found.")
    return customer

def get_all_customers():
    return session.query(Customer).order_by(Customer.name).all()


# UPDATE

def update_customer(customer_id, **kwargs):
    customer = get_customer_by_id(customer_id)
    for key, value in kwargs.items():
        if hasattr(customer, key):
            setattr(customer, key, value)
    session.commit()
    return customer


# DELETE

def delete_customer(customer_id):
    customer = get_customer_by_id(customer_id)
    session.delete(customer)
    session.commit()
    return True


# Business Logic Utilities

def add_loyalty_points(customer_id, points):
    customer = get_customer_by_id(customer_id)
    customer.loyalty_points += points
    session.commit()
    return customer

def apply_discount(customer_id, discount_percentage):
    customer = get_customer_by_id(customer_id)
    customer.discount_rate = discount_percentage
    session.commit()
    return customer
