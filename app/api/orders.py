from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import db, models, schemas
from ..auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.OrderOut)
def create_order(order_in: schemas.OrderCreate, db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    # create order
    order = models.Order(user_id=current_user.id)
    db.add(order)
    db.flush()
    items_out = []
    for it in order_in.items:
        product = db.query(models.Product).filter(models.Product.id == it.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {it.product_id} not found")
        if product.inventory < it.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough inventory for product {product.id}")
        product.inventory -= it.quantity
        order_item = models.OrderItem(order_id=order.id, product_id=product.id, quantity=it.quantity)
        db.add(order_item)
        items_out.append(order_item)
    db.commit()
    db.refresh(order)
    # return a plain dict with proper types for response validation
    return {
        "id": order.id,
        "user_id": order.user_id,
        "created_at": order.created_at,
        "items": [{"id": it.id, "product_id": it.product_id, "quantity": it.quantity} for it in order.items],
        "status": (order.status.value if getattr(order, "status", None) is not None else None)
    }

@router.get("/", response_model=List[schemas.OrderOut])
def list_orders(db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Order).filter(models.Order.user_id == current_user.id).all()


@router.get("/{order_id}", response_model=schemas.OrderDetailOut)
def get_order(order_id: int, db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    # only pending orders can be cancelled
    if getattr(order, 'status', None) != models.Order.OrderStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending orders can be cancelled")
    # restock
    for item in order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.inventory = (product.inventory or 0) + item.quantity
    order.status = models.Order.OrderStatus.cancelled
    db.commit()
    db.refresh(order)
    return {"ok": True, "order_id": order.id}
