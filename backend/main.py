from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend.database import init_db
from backend.api import categories, suppliers, products, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # при старте создаём таблицы
    yield


app = FastAPI(title="Warehouse IS", description="ИС учёта товаров на складе", lifespan=lifespan)

app.include_router(categories.router)
app.include_router(suppliers.router)
app.include_router(products.router)
app.include_router(transactions.router)


@app.get("/")
def root():
    return {"message": "Warehouse IS is running", "docs": "/docs"}
