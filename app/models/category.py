from sqlalchemy import Column, Integer, String
from . import Base
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(name={self.name}, description={self.description})>"
