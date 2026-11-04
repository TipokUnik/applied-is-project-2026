from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Supplier, SupplierCreate, SupplierRead

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("/", response_model=List[SupplierRead])
def list_suppliers(session: Session = Depends(get_session)):
    return session.exec(select(Supplier)).all()


@router.get("/{supplier_id}", response_model=SupplierRead)
def get_supplier(supplier_id: int, session: Session = Depends(get_session)):
    supplier = session.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Поставщик не найден")
    return supplier


@router.post("/", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
def create_supplier(data: SupplierCreate, session: Session = Depends(get_session)):
    supplier = Supplier.model_validate(data)
    session.add(supplier)
    session.commit()
    session.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, session: Session = Depends(get_session)):
    supplier = session.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Поставщик не найден")
    if supplier.products:
        raise HTTPException(status_code=409, detail="Нельзя удалить поставщика, у которого есть товары")
    session.delete(supplier)
    session.commit()
    return {"message": "Поставщик удалён"}
