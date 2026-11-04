from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401  (нужен, чтобы таблицы зарегистрировались в metadata)

sqlite_url = "sqlite:///database.db"
# echo=True выводит все SQL-запросы в консоль (удобно для отладки)
engine = create_engine(sqlite_url, echo=True, connect_args={"check_same_thread": False})


def init_db() -> None:
    """Создаёт все таблицы по ORM-моделям."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Зависимость FastAPI: открывает сессию на время запроса и закрывает её."""
    with Session(engine) as session:
        yield session
