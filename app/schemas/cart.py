from pydantic import BaseModel
from typing import List
from datetime import datetime

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartCreate(BaseModel):
    items: List[CartItemCreate] = []

class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        orm_mode = True

class CartOut(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    items: List[CartItemOut]

    class Config:
        orm_mode = True
