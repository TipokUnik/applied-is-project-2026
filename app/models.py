"""ORM-модели (таблицы БД) и Pydantic-схемы (валидация входных/выходных данных)."""
from datetime import datetime
from typing import List, Literal, Optional

from sqlmodel import Field, Relationship, SQLModel


# ---------- Category ----------
class CategoryBase(SQLModel):
    name: str = Field(min_length=1, index=True, unique=True)
    description: Optional[str] = None


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Связь: у одной категории много товаров
    products: List["Product"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int


# ---------- Supplier ----------
class SupplierBase(SQLModel):
    name: str = Field(min_length=1, index=True)
    phone: Optional[str] = None
    email: Optional[str] = None


class Supplier(SupplierBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # Связь: у одного поставщика много товаров
    products: List["Product"] = Relationship(back_populates="supplier")


class SupplierCreate(SupplierBase):
    pass


class SupplierRead(SupplierBase):
    id: int


# ---------- Product ----------
class ProductBase(SQLModel):
    name: str = Field(min_length=1, index=True)
    sku: str = Field(min_length=1, index=True, unique=True)  # артикул
    price: float = Field(ge=0)                               # цена не может быть отрицательной
    quantity: int = Field(default=0, ge=0)
    category_id: int = Field(foreign_key="category.id")      # внешний ключ
    supplier_id: int = Field(foreign_key="supplier.id")      # внешний ключ


class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Объектные связи (в БД это не колонки, а удобный доступ из Python)
    category: Optional[Category] = Relationship(back_populates="products")
    supplier: Optional[Supplier] = Relationship(back_populates="products")
    # При удалении товара удаляются и его записи в журнале
    logs: List["TransactionLog"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class ProductCreate(ProductBase):
    """Схема для POST: клиент не передаёт id."""


class ProductRead(ProductBase):
    id: int


class ProductUpdate(SQLModel):
    """Схема для PATCH: все поля необязательные."""
    name: Optional[str] = Field(default=None, min_length=1)
    sku: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, ge=0)
    quantity: Optional[int] = Field(default=None, ge=0)
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None


# ---------- TransactionLog ----------
class TransactionLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    type: str                                   # "in" (приход) или "out" (расход)
    amount: int = Field(gt=0)
    created_at: datetime = Field(default_factory=datetime.now)

    product: Optional[Product] = Relationship(back_populates="logs")


class TransactionCreate(SQLModel):
    product_id: int
    type: Literal["in", "out"]
    amount: int = Field(gt=0)


class TransactionRead(SQLModel):
    id: int
    product_id: int
    type: str
    amount: int
    created_at: datetime
