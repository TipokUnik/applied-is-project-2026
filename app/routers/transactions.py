from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Product, TransactionCreate, TransactionLog, TransactionRead

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=List[TransactionRead])
def list_transactions(product_id: Optional[int] = None, session: Session = Depends(get_session)):
    statement = select(TransactionLog)
    if product_id is not None:
        statement = statement.where(TransactionLog.product_id == product_id)
    return session.exec(statement).all()


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(data: TransactionCreate, session: Session = Depends(get_session)):
    """Приход ('in') увеличивает остаток, расход ('out') уменьшает."""
    product = session.get(Product, data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    if data.type == "in":
        product.quantity += data.amount
    else:
        if product.quantity < data.amount:
            raise HTTPException(status_code=400, detail="Недостаточно товара на складе")
        product.quantity -= data.amount

    log = TransactionLog(product_id=data.product_id, type=data.type, amount=data.amount)
    session.add(product)
    session.add(log)
    session.commit()
    session.refresh(log)
    return log
