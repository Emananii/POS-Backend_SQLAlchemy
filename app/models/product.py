from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models import Base

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)