from datetime import datetime
from sqlalchemy import text
from app.db.engine import engine, SessionLocal
from app.models import Base
from app.models.customer import Customer
from app.models.product import Product
from app.models.category import Category
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from sqlalchemy import text

def seed_default_customer():
    print("Creating tables if they don't exist...")

    Base.metadata.create_all(engine)

    session = SessionLocal()
    print("Checking if 'Walk-In' customer exists...")
    walk_in = session.query(Customer).filter_by(name="Walk-In").first()
    if not walk_in:
        print("Walk-In customer not found, adding it...")
        walk_in = Customer(name="Walk-In", email="walkin@gmail.com")
        session.add(walk_in)
        session.commit()
    else:
        print("Walk-in Customer already exists.")
    
    session.close()

def seed_default_categories():
    session = SessionLocal()
    categories = ["Beverages", "Grocery", "Snacks", "Frozen Foods", "Dairy"]
    
    for category_name in categories:
        category = session.query(Category).filter_by(name=category_name).first()
        if not category:
            print(f"Adding category: {category_name}")
            category = Category(name=category_name)
            session.add(category)
    
    session.commit()
    session.close()

def seed_default_product():
    print("Creating tables if they don't exist...")

  
    Base.metadata.create_all(engine)

    session = SessionLocal()
   
    category = session.query(Category).filter_by(name="Beverages").first()
    if not category:
        print("Category 'Beverages' not found! Please seed categories first.")
    else:
        print("Category 'Beverages' found, proceeding to add product.")


    product = session.query(Product).filter_by(name="Coca-Cola").first()
    if not product:
        print("Product Coca-Cola not found, adding it...")

        
        product = Product(
            name="Coca-Cola",
            brand="Coca-Cola",
            purchase_price=108,
            selling_price=120,
            stock=50,
            image="https://images.unsplash.com/photo-1622708862830-a026e3ef60bd?q=80&w=2564&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            barcode="5449000000996",
            category_id=category.id,  
            unit="ml"
        )
        session.add(product)
        session.commit()
    else:
        print("Product Coca-Cola already exists.")
    
    session.close()


def show_tables():
    print("Showing tables in the database:")
    session = SessionLocal()
    tables = session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
    for table in tables:
        print(table[0])
    session.close()

def seed_sales_and_sale_items():
    session = SessionLocal()

    # Fetch Walk-In customer
    walk_in_customer = session.query(Customer).filter_by(name="Walk-In").first()
    if not walk_in_customer:
        print("Walk-In customer not found! Cannot seed sales.")
        session.close()
        return

    # Fetch product
    product = session.query(Product).filter_by(name="Coca-Cola").first()
    if not product:
        print("Product 'Coca-Cola' not found! Cannot seed sales.")
        session.close()
        return

    # Check if a similar sale already exists to prevent duplicates
    existing_sale = (
        session.query(Sale)
        .filter_by(customer_id=walk_in_customer.id, total_amount=product.selling_price)
        .join(Sale.items)
        .filter(SaleItem.product_id == product.id)
        .first()
    )

    if existing_sale:
        print("A similar sale already exists. Skipping seeding this sale.")
        session.close()
        return

    # Create Sale
    sale = Sale(
        customer_id=walk_in_customer.id,
        total_amount=product.selling_price  # Assuming 1 quantity for simplicity
    )
    session.add(sale)
    session.flush()  # Get generated ID

    # Create SaleItem
    sale_item = SaleItem(
        sale_id=sale.id,
        product_id=product.id,
        name=product.name,
        quantity=1,
        price_at_sale=product.selling_price
    )
    session.add(sale_item)

    # Commit changes
    session.commit()
    print(f"Seeded 1 sale with 1 item for customer '{walk_in_customer.name}'")

    session.close()



if __name__ == "__main__":
    seed_default_categories()  
    seed_default_product()     
    seed_default_customer()  
    show_tables()      
    seed_sales_and_sale_items()       
    print("Seeding complete.")
