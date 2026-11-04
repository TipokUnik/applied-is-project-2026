from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.routers import categories, products, suppliers, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # при старте создаём таблицы, если их ещё нет
    yield


app = FastAPI(
    title="Warehouse IS",
    description="ИС учёта товаров на складе",
    lifespan=lifespan,
)

app.include_router(categories.router)
app.include_router(suppliers.router)
app.include_router(products.router)
app.include_router(transactions.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Warehouse IS is running", "docs": "/docs"}
