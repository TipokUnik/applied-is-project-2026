from typing import Optional
from sqlmodel import SQLModel, Field


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    sku: str = Field(unique=True, index=True)  # артикул
    price: float = Field(ge=0)
    quantity: int = Field(default=0, ge=0)
    category_id: int = Field(foreign_key="category.id")   # связь N:1 с Category
    supplier_id: int = Field(foreign_key="supplier.id")   # связь N:1 с Supplier
