from sqlmodel import SQLModel, Session, create_engine

# SQLite-файл создастся автоматически в корне проекта
DATABASE_URL = "sqlite:///warehouse.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    """Создаёт все таблицы по моделям."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Зависимость FastAPI: выдаёт сессию БД на время запроса."""
    with Session(engine) as session:
        yield session
