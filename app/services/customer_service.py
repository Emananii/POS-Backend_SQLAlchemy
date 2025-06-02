from sqlalchemy.exc import IntegrityError
from app.models.customer import Customer
from app.models.sale import Sale
from app.db.engine import SessionLocal

def create_customer(db, name, email, phone=None, customer_type="individual", company_name=None, discount_rate=0):
    customer = Customer(
        name=name,
        email=email,
        phone=phone,
        customer_type=customer_type,
        company_name=company_name,
        discount_rate=discount_rate
    )
    try:
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
    except IntegrityError:
        db.rollback()
        raise ValueError("A customer with this email already exists.")

def get_customer_by_id(db, customer_id):
        customer = db.query(Customer).get(customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        return customer


def get_customer_by_email(db, email):
        customer = db.query(Customer).filter_by(email=email).first()
        if not customer:
            raise ValueError(f"Customer with email '{email}' not found.")
        return customer
    
def get_customer_by_name(db, name):
    return db.query(Customer).filter(Customer.name.ilike(f"%{name}%")).all()

def get_all_customers(db):
    return db.query(Customer).order_by(Customer.name).all()

def get_purchases_by_customer(db, customer_id: int):
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return None
        sales = db.query(Sale).filter(Sale.customer_id == customer_id).all()
        return sales

def update_customer(db, customer_id, **kwargs):
        customer = db.query(Customer).get(customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        for key, value in kwargs.items():
            if hasattr(customer, key):
                setattr(customer, key, value)

        db.commit()
        db.refresh(customer)
        return customer


def delete_customer(db, customer_id):
        customer = db.query(Customer).get(customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")

        db.delete(customer)
        db.commit()
        return True

def add_loyalty_points(db, customer_id, points):
        customer = db.query(Customer).get(customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        customer.loyalty_points += points
        db.commit()
        db.refresh(customer)
        return customer


def apply_discount(db, customer_id, discount_percentage):
        customer = db.query(Customer).get(customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        customer.discount_rate = discount_percentage
        db.commit()
        db.refresh(customer)
        return customer