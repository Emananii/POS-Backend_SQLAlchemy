from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.models.customer import Customer
#from app.models.sale import Sale
from app.models.product import Product
from app.models.sale_item import SaleItem
from app.models.category import Category

DATABASE_URL = "sqlite:///pos.db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)


session = SessionLocal()