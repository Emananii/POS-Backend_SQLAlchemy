from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, DateTime, ForeignKey,
    CheckConstraint, PrimaryKeyConstraint, Index
)
from sqlalchemy.orm import relationship
from app.db.engine import Base, SessionLocal
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale_item import SaleItem


# ORM Model for Sale
class Sale(Base):
    __tablename__ = 'sales'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_sales_id'),
        CheckConstraint('total_amount >= 0', name='check_total_amount_positive'),
        Index('idx_sales_customer_id', 'customer_id'),
        Index('idx_sales_timestamp', 'timestamp'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)

    customer = relationship("Customer", backref="sales")

    def __repr__(self):
        return f"<Sale id={self.id} customer_id={self.customer_id} total_amount={self.total_amount}>"


# Business logic for managing sales
class Sales:
    def __init__(self):
        self.items = []

    def add_item(self, product, quantity):
        if product.stock >= quantity:
            self.items.append((product, quantity))
        else:
            raise ValueError(f"Not enough stock for '{product.name}'")

    def view_cart(self):
        return [(p.name, qty, p.price * qty) for p, qty in self.items]

    def total_price(self):
        return sum(p.price * qty for p, qty in self.items)

    def checkout(self, customer_email=None, customer_info=None):
        session = SessionLocal()

        # Retrieve or create customer
        customer = None
        if customer_email:
            customer = session.query(Customer).filter_by(email=customer_email).first()
            if not customer and customer_info:
                customer = Customer(**customer_info)
                session.add(customer)
                session.commit()

        # Calculate total amount for the sale
        total_amount = self.total_price()

        # Create Sale record
        sale = Sale(customer_id=customer.id if customer else None, timestamp=datetime.utcnow(), total_amount=total_amount)
        session.add(sale)

        for product, quantity in self.items:
            if product.stock < quantity:
                raise ValueError(f"Insufficient stock for {product.name}")

            product.stock -= quantity

            sale_item = SaleItem(
                sale=sale,
                product_id=product.id,
                quantity=quantity,
                subtotal=product.price * quantity
            )
            session.add(sale_item)

        session.commit()
        self.items.clear()
        session.close()

        return sale
