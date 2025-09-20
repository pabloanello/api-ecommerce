from pydantic import BaseModel, validator
from typing import List
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        orm_mode = True

class OrderOut(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    items: List[OrderItemOut]
    status: str

    @validator('status', pre=True, always=True)
    def status_to_str(cls, v):
        if hasattr(v, 'value'):
            return v.value
        return str(v)

    class Config:
        orm_mode = True

class OrderDetailOut(OrderOut):
    pass
