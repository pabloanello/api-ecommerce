from app.schemas.user import UserCreate, UserOut
from app.schemas.product import ProductBase, ProductCreate, ProductOut
from app.schemas.order import OrderItemCreate, OrderCreate, OrderItemOut, OrderOut
from app.schemas.cart import CartItemCreate, CartCreate, CartItemOut, CartOut
from app.schemas.token import Token
from datetime import datetime
import pytest

def test_user_create_schema():
    data = {"email": "a@b.com", "password": "secret"}
    user = UserCreate(**data)
    assert user.email == "a@b.com"
    assert user.password == "secret"

def test_user_out_schema():
    data = {"id": 1, "email": "a@b.com", "is_active": True, "created_at": datetime.utcnow()}
    user = UserOut(**data)
    assert user.id == 1
    assert user.is_active is True

def test_product_base_and_out_schema():
    base = ProductBase(title="T", price=1.5)
    assert base.title == "T"
    assert base.price == 1.5
    out = ProductOut(id=1, title="T", price=1.5)
    assert out.id == 1

def test_order_item_create_and_out_schema():
    item = OrderItemCreate(product_id=2, quantity=3)
    assert item.product_id == 2
    assert item.quantity == 3
    out = OrderItemOut(id=1, product_id=2, quantity=3)
    assert out.id == 1

def test_order_create_and_out_schema():
    items = [OrderItemCreate(product_id=2, quantity=3)]
    order = OrderCreate(items=items)
    assert order.items[0].product_id == 2
    out = OrderOut(id=1, user_id=1, created_at=datetime.utcnow(), items=[], status="pending")
    assert out.status == "pending"

def test_cart_item_create_and_out_schema():
    item = CartItemCreate(product_id=2, quantity=4)
    assert item.product_id == 2
    out = CartItemOut(id=1, product_id=2, quantity=4)
    assert out.id == 1

def test_cart_create_and_out_schema():
    items = [CartItemCreate(product_id=2, quantity=4)]
    cart = CartCreate(items=items)
    assert cart.items[0].product_id == 2
    out = CartOut(id=1, user_id=1, created_at=datetime.utcnow(), items=[])
    assert out.id == 1

def test_token_schema():
    token = Token(access_token="abc123")
    assert token.access_token == "abc123"
    assert token.token_type == "bearer"
