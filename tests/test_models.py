import pytest
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderStatus, OrderItem
from app.models.cart import Cart, CartItem
from datetime import datetime

def test_user_model_fields():
    user = User(email="a@b.com", hashed_password="hash", is_active=1, created_at=datetime.utcnow())
    assert user.email == "a@b.com"
    assert user.hashed_password == "hash"
    assert user.is_active == 1
    assert isinstance(user.created_at, datetime)

def test_product_model_fields():
    product = Product(title="Test", description="desc", price=9.99, inventory=5)
    assert product.title == "Test"
    assert product.description == "desc"
    assert product.price == 9.99
    assert product.inventory == 5

def test_order_status_enum():
    assert OrderStatus.pending.value == "pending"
    assert OrderStatus.completed.value == "completed"
    assert OrderStatus.cancelled.value == "cancelled"

def test_order_model_fields():
    order = Order(user_id=1, status=OrderStatus.pending, created_at=datetime.utcnow())
    assert order.user_id == 1
    assert order.status == OrderStatus.pending
    assert isinstance(order.created_at, datetime)

def test_order_item_model_fields():
    item = OrderItem(order_id=1, product_id=2, quantity=3)
    assert item.order_id == 1
    assert item.product_id == 2
    assert item.quantity == 3

def test_cart_model_fields():
    cart = Cart(user_id=1, created_at=datetime.utcnow())
    assert cart.user_id == 1
    assert isinstance(cart.created_at, datetime)

def test_cart_item_model_fields():
    item = CartItem(cart_id=1, product_id=2, quantity=4)
    assert item.cart_id == 1
    assert item.product_id == 2
    assert item.quantity == 4
