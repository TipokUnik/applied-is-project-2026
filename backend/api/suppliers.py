from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import Supplier

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post("/", response_model=Supplier)
def create_supplier(supplier: Supplier, session: Session = Depends(get_session)):
    session.add(supplier)
    session.commit()
    session.refresh(supplier)
    return supplier


@router.get("/", response_model=List[Supplier])
def list_suppliers(session: Session = Depends(get_session)):
    return session.exec(select(Supplier)).all()


@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, session: Session = Depends(get_session)):
    supplier = session.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(404, "Поставщик не найден")
    session.delete(supplier)
    session.commit()
    return {"ok": True}
