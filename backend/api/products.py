from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import Product, Category, Supplier

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=Product)
def create_product(product: Product, session: Session = Depends(get_session)):
    if not session.get(Category, product.category_id):
        raise HTTPException(400, "Такой категории нет")
    if not session.get(Supplier, product.supplier_id):
        raise HTTPException(400, "Такого поставщика нет")
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.get("/", response_model=List[Product])
def list_products(session: Session = Depends(get_session)):
    return session.exec(select(Product)).all()


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Товар не найден")
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Товар не найден")
    session.delete(product)
    session.commit()
    return {"ok": True}
