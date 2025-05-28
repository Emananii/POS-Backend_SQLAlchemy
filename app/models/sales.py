from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, Float, DateTime, ForeignKey,
    CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from app.db.engine import Base


class Sale(Base):
    __tablename__ = 'sales'
    __table_args__ = (
        CheckConstraint('total_amount >= 0', name='check_total_amount_positive'),
        Index('idx_sales_customer_id', 'customer_id'),
        Index('idx_sales_timestamp', 'timestamp'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    total_amount = Column(Float, nullable=False)

    customer = relationship("Customer", backref="sales")

    def __repr__(self):
        return f"<Sale id={self.id} customer_id={self.customer_id} total_amount={self.total_amount}>"