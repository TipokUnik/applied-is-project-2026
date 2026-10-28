from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import Product, TransactionLog

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionLog)
def create_transaction(log: TransactionLog, session: Session = Depends(get_session)):
    """Приход ('in') увеличивает остаток, расход ('out') уменьшает."""
    product = session.get(Product, log.product_id)
    if not product:
        raise HTTPException(404, "Товар не найден")
    if log.type not in ("in", "out"):
        raise HTTPException(400, "type должен быть 'in' или 'out'")

    if log.type == "in":
        product.quantity += log.amount
    else:
        if product.quantity < log.amount:
            raise HTTPException(400, "Недостаточно товара на складе")
        product.quantity -= log.amount

    session.add(product)
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


@router.get("/", response_model=List[TransactionLog])
def list_transactions(session: Session = Depends(get_session)):
    return session.exec(select(TransactionLog)).all()
