from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..db.base import Base

class OrderStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(SAEnum(OrderStatus), default=OrderStatus.pending)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
