from sqlalchemy import (
    Column, String, Integer,
    CheckConstraint, PrimaryKeyConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customers'

    __table_args__ = (
        CheckConstraint('email != ""', name='check_email_not_empty'),
        PrimaryKeyConstraint('id', name='pk_customer_id'),
        UniqueConstraint('email', name='uq_customer_email'),
        Index('idx_customer_name', 'name'),
        Index('idx_customer_email', 'email')
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(15), nullable=True)

    customer_type = Column(String(50), default='individual')  # or 'business'
    company_name = Column(String(100), nullable=True)
    loyalty_points = Column(Integer, default=0)
    discount_rate = Column(Integer, default=0)  # Percentage discount

    def __repr__(self):
        return f"<Customer id={self.id}, name='{self.name}', email='{self.email}'>"
