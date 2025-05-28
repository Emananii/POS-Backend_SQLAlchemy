from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models import Base
class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)