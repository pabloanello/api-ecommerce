from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...db import deps
from ...models import Order, User, OrderItem, Product, OrderStatus
from ...schemas import OrderCreate, OrderOut, OrderDetailOut
from ...core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=OrderOut)
def create_order(
    order: OrderCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(get_current_active_user)
):
    """
    Create new order.
    """
    db_order = Order(user_id=current_user.id)
    db.add(db_order)
    db.flush()
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
        if product.inventory < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough inventory for product {product.id}")
        product.inventory -= item.quantity
        order_item = OrderItem(order_id=db_order.id, product_id=product.id, quantity=item.quantity)
        db.add(order_item)
    db.commit()
    db.refresh(db_order)
    return OrderOut.from_orm(db_order)


@router.get("/", response_model=List[OrderOut])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db), current_user: User = Depends(get_current_active_user)):
    """
    Retrieve orders.
    """
    orders = db.query(Order).filter(Order.owner_id == current_user.id).offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=OrderDetailOut)
def read_order(order_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(get_current_active_user)):
    """
    Retrieve order by ID.
    """
    order = db.query(Order).filter(Order.id == order_id, Order.owner_id == current_user.id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}", response_model=OrderOut)
def update_order(order_id: int, order: OrderCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(get_current_active_user)):
    """
    Update an order.
    """
    db_order = db.query(Order).filter(Order.id == order_id, Order.owner_id == current_user.id)
    if db_order.first() is None:
        raise HTTPException(status_code=404, detail="Order not found")
    db_order.update(order.dict())
    db.commit()
    return db_order.first()


@router.delete("/{order_id}", response_model=OrderOut)
def delete_order(order_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(get_current_active_user)):
    """
    Delete an order.
    """
    db_order = db.query(Order).filter(Order.id == order_id, Order.owner_id == current_user.id)
    if db_order.first() is None:
        raise HTTPException(status_code=404, detail="Order not found")
    db_order.delete()
    db.commit()
    return db_order.first()


@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(get_current_active_user)):
    """
    Cancel an order.
    """
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    # only pending orders can be cancelled
    if getattr(order, 'status', None) != OrderStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending orders can be cancelled")
    # restock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.inventory = (product.inventory or 0) + item.quantity
    order.status = OrderStatus.cancelled
    db.commit()
    db.refresh(order)
    return {"ok": True, "order_id": order.id}
