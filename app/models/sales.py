from datetime import datetime
from sqlalchemy.orm import Session
from models import Product, Customer, Sale, SaleItem
from database import Session as DBSession

class Cart:
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
        session = DBSession()

        # Retrieve or create customer
        customer = None
        if customer_email:
            customer = session.query(Customer).filter_by(email=customer_email).first()
            if not customer and customer_info:
                customer = Customer(**customer_info)
                session.add(customer)
                session.commit()

        # Create Sale
        sale = Sale(customer_id=customer.id if customer else None, timestamp=datetime.now())
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
