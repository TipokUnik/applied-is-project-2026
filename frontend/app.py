import pandas as pd
import requests
import streamlit as st

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Склад", page_icon="📦", layout="wide")
st.title("📦 ИС учёта товаров на складе")


def get(path):
    try:
        return requests.get(f"{API}{path}", timeout=5).json()
    except requests.exceptions.RequestException:
        st.error("Backend не запущен. Запустите: uvicorn backend.main:app --reload")
        st.stop()


def post(path, data):
    r = requests.post(f"{API}{path}", json=data, timeout=5)
    if r.ok:
        st.success("Готово!")
    else:
        st.error(r.json().get("detail", "Ошибка"))


page = st.sidebar.radio("Раздел", ["Товары", "Категории", "Поставщики", "Движение товара"])

if page == "Товары":
    st.subheader("Список товаров")
    products = get("/products/")
    if products:
        st.dataframe(pd.DataFrame(products), use_container_width=True)
    else:
        st.info("Товаров пока нет")

    st.subheader("Добавить товар")
    cats, sups = get("/categories/"), get("/suppliers/")
    if not cats or not sups:
        st.warning("Сначала добавьте хотя бы одну категорию и одного поставщика")
    else:
        with st.form("product_form"):
            name = st.text_input("Название")
            sku = st.text_input("Артикул (SKU)")
            price = st.number_input("Цена", min_value=0.0, step=1.0)
            quantity = st.number_input("Количество", min_value=0, step=1)
            cat = st.selectbox("Категория", cats, format_func=lambda c: c["name"])
            sup = st.selectbox("Поставщик", sups, format_func=lambda s: s["name"])
            if st.form_submit_button("Добавить"):
                post("/products/", {"name": name, "sku": sku, "price": price,
                                    "quantity": quantity,
                                    "category_id": cat["id"], "supplier_id": sup["id"]})

elif page == "Категории":
    st.subheader("Категории")
    cats = get("/categories/")
    if cats:
        st.dataframe(pd.DataFrame(cats), use_container_width=True)
    with st.form("cat_form"):
        name = st.text_input("Название категории")
        desc = st.text_input("Описание")
        if st.form_submit_button("Добавить"):
            post("/categories/", {"name": name, "description": desc})

elif page == "Поставщики":
    st.subheader("Поставщики")
    sups = get("/suppliers/")
    if sups:
        st.dataframe(pd.DataFrame(sups), use_container_width=True)
    with st.form("sup_form"):
        name = st.text_input("Название")
        phone = st.text_input("Телефон")
        email = st.text_input("Email")
        if st.form_submit_button("Добавить"):
            post("/suppliers/", {"name": name, "phone": phone, "email": email})

else:
    st.subheader("Приход / расход товара")
    products = get("/products/")
    if products:
        with st.form("tr_form"):
            prod = st.selectbox("Товар", products, format_func=lambda p: f"{p['name']} (остаток {p['quantity']})")
            kind = st.radio("Тип операции", ["in", "out"], format_func=lambda k: "Приход" if k == "in" else "Расход")
            amount = st.number_input("Количество", min_value=1, step=1)
            if st.form_submit_button("Провести"):
                post("/transactions/", {"product_id": prod["id"], "type": kind, "amount": amount})
    st.subheader("Журнал операций")
    logs = get("/transactions/")
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True)
