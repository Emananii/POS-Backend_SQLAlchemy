from sqlalchemy import (
    Column, Integer, Float, String, DateTime,
    ForeignKey, CheckConstraint, PrimaryKeyConstraint, Index
)
from sqlalchemy.orm import relationship
from app.models import Base
from datetime import datetime

class Sale(Base):
    __tablename__ = 'sales'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_sales_id'),
        CheckConstraint('total_amount >= 0', name='check_total_amount_positive'),
        Index('idx_sales_customer_id', 'customer_id'),
        Index('idx_sales_timestamp', 'timestamp')
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)

    # Optional: relationship to access customer directly
    customer = relationship("Customer", backref="sales")

    def __repr__(self):
        return f"<Sale id={self.id} customer_id={self.customer_id} total_amount={self.total_amount}>"
