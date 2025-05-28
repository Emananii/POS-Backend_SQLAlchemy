from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models import Base

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer)
    #Will change back to this: sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False) : once Sale model is defined
    product_id = Column(Integer)
    #Will change back to this: product_id = Column(Integer, ForeignKey("products.id"), nullable=False) : once Product model is defined
    
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_sale = Column(Integer, nullable=False)


    #Will uncomment these when Sale and Product models are defined
    #sale = relationship("Sale", back_populates="items")
    #product = relationship("Product")
    
    def __repr__(self):
        return f"<SaleItem id={self.id}, sale_id={self.sale_id}, name='{self.name}', qty={self.quantity}>"
