from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.engine import Base

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_sale = Column(Float, nullable=False)
   
    sale = relationship("Sale", back_populates="items")

    product = relationship("Product")

    def __repr__(self):
        return f"<SaleItem id={self.id}, sale_id={self.sale_id}, name='{self.name}', qty={self.quantity}>"
