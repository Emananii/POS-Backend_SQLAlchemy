from sqlalchemy import Column, Integer, String, Float, ForeignKey
from . import Base
from app.models.category import Category
from sqlalchemy.orm import relationship

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
    category_id = Column(Integer, ForeignKey('categories.id'))
    unit = Column(String)

    category = relationship("Category", back_populates="products")
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
            "category": self.category.name if self.category else None,
            "unit": self.unit
        }
