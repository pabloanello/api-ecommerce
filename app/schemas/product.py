from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    inventory: int = 0

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int

    class Config:
        orm_mode = True
