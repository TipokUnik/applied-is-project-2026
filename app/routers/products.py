from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from app.db import get_session
from app.models import (
    Category,
    Product,
    ProductCreate,
    ProductRead,
    ProductUpdate,
    Supplier,
)

router = APIRouter(prefix="/products", tags=["Products"])


# ---------- ЛР3: чтение ----------
@router.get("/", response_model=List[ProductRead])
def list_products(
    search: Optional[str] = None,       # часть названия
    min_price: Optional[float] = None,  # цена от
    max_price: Optional[float] = None,  # цена до
    category_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    """Список товаров. Все параметры необязательные (ЛР4: фильтрация и поиск)."""
    statement = select(Product)
    if search:
        statement = statement.where(col(Product.name).contains(search))
    if min_price is not None:
        statement = statement.where(Product.price >= min_price)
    if max_price is not None:
        statement = statement.where(Product.price <= max_price)
    if category_id is not None:
        statement = statement.where(Product.category_id == category_id)
    return session.exec(statement).all()


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product


# ---------- ЛР3: создание ----------
@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, session: Session = Depends(get_session)):
    if not session.get(Category, data.category_id):
        raise HTTPException(status_code=400, detail="Такой категории нет")
    if not session.get(Supplier, data.supplier_id):
        raise HTTPException(status_code=400, detail="Такого поставщика нет")

    product = Product.model_validate(data)
    session.add(product)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Товар с таким артикулом уже существует")
    session.refresh(product)
    return product


# ---------- ЛР4: частичное обновление ----------
@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    data: ProductUpdate,
    session: Session = Depends(get_session),
):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # берём только то, что прислал клиент, и отбрасываем None
    update_data = {
        key: value
        for key, value in data.model_dump(exclude_unset=True).items()
        if value is not None
    }
    if "category_id" in update_data and not session.get(Category, update_data["category_id"]):
        raise HTTPException(status_code=400, detail="Такой категории нет")
    if "supplier_id" in update_data and not session.get(Supplier, update_data["supplier_id"]):
        raise HTTPException(status_code=400, detail="Такого поставщика нет")

    db_product.sqlmodel_update(update_data)
    session.add(db_product)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Товар с таким артикулом уже существует")
    session.refresh(db_product)
    return db_product


# ---------- ЛР4: удаление ----------
@router.delete("/{product_id}")
def delete_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    session.delete(product)
    session.commit()
    return {"message": f"Товар {product_id} удалён"}
