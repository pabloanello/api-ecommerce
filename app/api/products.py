from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import db, models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.ProductOut)
def create_product(product_in: schemas.ProductCreate, db: Session = Depends(db.get_db)):
    product = models.Product(**product_in.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/", response_model=List[schemas.ProductOut])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(db.get_db)):
    return db.query(models.Product).offset(skip).limit(limit).all()

@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(db.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, product_in: schemas.ProductCreate, db: Session = Depends(db.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product_in.dict().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(db.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"ok": True}
