from sqlalchemy import Column, Integer, String, Text, Float
from ..db.base import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    inventory = Column(Integer, default=0)
