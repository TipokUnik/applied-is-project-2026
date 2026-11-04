"""Наполнение БД тестовыми данными. Запуск: python seed.py"""
from sqlmodel import Session, select

from app.db import engine, init_db
from app.models import Category, Product, Supplier, TransactionLog


def seed() -> None:
    init_db()
    with Session(engine) as session:
        if session.exec(select(Category)).first():
            print("База уже содержит данные, посев пропущен.")
            return

        # --- категории ---
        electronics = Category(name="Электроника", description="Техника и гаджеты")
        office = Category(name="Канцелярия", description="Товары для офиса")
        furniture = Category(name="Мебель", description="Столы и стулья")
        session.add_all([electronics, office, furniture])

        # --- поставщики ---
        tehno = Supplier(name="ООО Техносклад", phone="+7 700 111 22 33", email="info@tehno.kz")
        paper = Supplier(name="Бумажный мир", phone="+7 701 222 33 44", email="sales@paper.kz")
        mebel = Supplier(name="МебельПром", phone="+7 702 333 44 55", email="order@mebel.kz")
        session.add_all([tehno, paper, mebel])

        # --- товары (связи задаём через объекты, а не через id) ---
        products = [
            Product(name="Ноутбук Lenovo", sku="NB-001", price=450000, quantity=10,
                    category=electronics, supplier=tehno),
            Product(name="Монитор Samsung 24", sku="MN-002", price=95000, quantity=15,
                    category=electronics, supplier=tehno),
            Product(name="Бумага А4 (500 л.)", sku="PP-003", price=2500, quantity=200,
                    category=office, supplier=paper),
            Product(name="Ручка шариковая", sku="PN-004", price=150, quantity=500,
                    category=office, supplier=paper),
            Product(name="Офисный стул", sku="CH-005", price=35000, quantity=20,
                    category=furniture, supplier=mebel),
        ]
        session.add_all(products)
        session.flush()  # отправляем в БД, чтобы у объектов появились id

        # --- журнал: начальный приход каждого товара ---
        logs = [TransactionLog(product=p, type="in", amount=p.quantity) for p in products]
        session.add_all(logs)

        session.commit()
        print("Готово: добавлено 3 категории, 3 поставщика, 5 товаров, 5 записей журнала.")


if __name__ == "__main__":
    seed()
