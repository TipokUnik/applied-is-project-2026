from typing import Optional
from sqlmodel import SQLModel, Field


class Supplier(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    phone: Optional[str] = None
    email: Optional[str] = None
