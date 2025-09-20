from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...db import deps
from ...models import Product
from ...schemas import ProductCreate, ProductOut

router = APIRouter()


@router.post("/", response_model=ProductOut)
def create_product(
    product: ProductCreate, db: Session = Depends(deps.get_db)
):
    """
    Create new product.
    """
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/", response_model=List[ProductOut])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    """
    Retrieve products.
    """
    products = db.query(Product).offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductOut)
def read_product(product_id: int, db: Session = Depends(deps.get_db)):
    """
    Retrieve a product by ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int, product: ProductCreate, db: Session = Depends(deps.get_db)
):
    """
    Update a product.
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(deps.get_db)):
    """
    Delete a product.
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"ok": True}
