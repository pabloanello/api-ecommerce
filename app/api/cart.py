from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import db, models, schemas
from ..auth import get_current_user

router = APIRouter()


def _get_or_create_cart(db: Session, user: models.User):
    cart = db.query(models.Cart).filter(models.Cart.user_id == user.id).first()
    if not cart:
        cart = models.Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


@router.get("/", response_model=schemas.CartOut)
def get_cart(db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    return cart


@router.post("/items", response_model=schemas.CartOut)
def add_cart_item(item_in: schemas.CartItemCreate, db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    product = db.query(models.Product).filter(models.Product.id == item_in.product_id).first()
    if not product:
        raise HTTPException(status_code=400, detail="Product not found")
    # find existing cart item
    ci = db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id, models.CartItem.product_id == product.id).first()
    if ci:
        ci.quantity += item_in.quantity
    else:
        ci = models.CartItem(cart_id=cart.id, product_id=product.id, quantity=item_in.quantity)
        db.add(ci)
    db.commit()
    db.refresh(cart)
    return cart


@router.delete("/items/{item_id}", response_model=schemas.CartOut)
def remove_cart_item(item_id: int, db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    ci = db.query(models.CartItem).filter(models.CartItem.id == item_id, models.CartItem.cart_id == cart.id).first()
    if not ci:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(ci)
    db.commit()
    db.refresh(cart)
    return cart


@router.patch("/items/{item_id}", response_model=schemas.CartOut)
def update_cart_item(item_id: int, item_in: schemas.CartItemCreate, db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    ci = db.query(models.CartItem).filter(models.CartItem.id == item_id, models.CartItem.cart_id == cart.id).first()
    if not ci:
        raise HTTPException(status_code=404, detail="Cart item not found")
    if item_in.quantity <= 0:
        db.delete(ci)
    else:
        ci.quantity = item_in.quantity
    db.commit()
    db.refresh(cart)
    return cart


@router.post("/clear", response_model=schemas.CartOut)
def clear_cart(db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    # delete all items
    for ci in list(cart.items):
        db.delete(ci)
    db.commit()
    db.refresh(cart)
    return cart


@router.get("/items/{item_id}", response_model=schemas.CartItemOut)
def get_cart_item(item_id: int, db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    ci = db.query(models.CartItem).filter(models.CartItem.id == item_id, models.CartItem.cart_id == cart.id).first()
    if not ci:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return ci


@router.delete("/items/product/{product_id}", response_model=schemas.CartOut)
def remove_item_by_product(product_id: int, db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    ci = db.query(models.CartItem).filter(models.CartItem.product_id == product_id, models.CartItem.cart_id == cart.id).first()
    if not ci:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(ci)
    db.commit()
    db.refresh(cart)
    return cart


@router.put("/items/product/{product_id}", response_model=schemas.CartOut)
def set_quantity_by_product(product_id: int, item_in: schemas.CartItemCreate, db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=400, detail="Product not found")
    ci = db.query(models.CartItem).filter(models.CartItem.product_id == product_id, models.CartItem.cart_id == cart.id).first()
    if item_in.quantity <= 0:
        if ci:
            db.delete(ci)
    else:
        if ci:
            ci.quantity = item_in.quantity
        else:
            ci = models.CartItem(cart_id=cart.id, product_id=product_id, quantity=item_in.quantity)
            db.add(ci)
    db.commit()
    db.refresh(cart)
    return cart


@router.get("/summary")
def cart_summary(db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    cart = _get_or_create_cart(db, current_user)
    total_items = sum(ci.quantity for ci in cart.items)
    total_price = 0.0
    for ci in cart.items:
        p = db.query(models.Product).filter(models.Product.id == ci.product_id).first()
        if p:
            total_price += (p.price or 0.0) * ci.quantity
    return {"id": cart.id, "user_id": cart.user_id, "total_items": total_items, "total_price": total_price}


@router.post("/checkout")
def checkout(db: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    cart = db.query(models.Cart).filter(models.Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # verify inventory
    for ci in cart.items:
        product = db.query(models.Product).filter(models.Product.id == ci.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {ci.product_id} not found")
        if product.inventory < ci.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough inventory for product {product.id}")

    # create order
    order = models.Order(user_id=current_user.id)
    db.add(order)
    db.flush()
    for ci in list(cart.items):
        product = db.query(models.Product).filter(models.Product.id == ci.product_id).first()
        product.inventory -= ci.quantity
        oi = models.OrderItem(order_id=order.id, product_id=product.id, quantity=ci.quantity)
        db.add(oi)
        # remove cart item
        db.delete(ci)

    db.commit()
    db.refresh(order)
    return {"ok": True, "order_id": order.id}
