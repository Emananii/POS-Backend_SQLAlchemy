from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
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
    category = Column(String)  # consider changing to category_id FK later
    unit = Column(String)

    # Relationship to sale items
    sale_items = relationship("SaleItem", back_populates="product")

    def __repr__(self):
        return f"<Product(name={self.name}, price={self.selling_price}, stock={self.stock})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "purchase_price": self.purchase_price,
            "selling_price": self.selling_price,
            "stock": self.stock,
            "image": self.image,
            "barcode": self.barcode,
            "category": self.category,
            "unit": self.unit
        }