# app/models/product.py
from sqlalchemy import Column, Integer, String, Float
from . import Base

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    purchase_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    image = Column(String)
    barcode = Column(String, unique=True)
    category = Column(String)
    unit = Column(String)

    def __repr__(self):
        return f"<Product(name={self.name}, price={self.selling_price}, stock={self.stock})>"
