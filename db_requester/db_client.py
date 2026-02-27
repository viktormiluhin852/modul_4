from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from resources.db_creds import MoviesDbCreds
from contextlib import contextmanager
from typing import Generator
import allure

class DBClient:
    """Клиент для работы с подключением к БД — создаёт engine и фабрику сессий."""

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        host: str | None = None,
        port: str | None = None,
        database: str | None = None,
        echo: bool = False,
    ):

        username = username or MoviesDbCreds.USERNAME
        password = password or MoviesDbCreds.PASSWORD
        host = host or MoviesDbCreds.HOST
        port = port or MoviesDbCreds.PORT
        database = database or MoviesDbCreds.DATABASE_NAME
        self.engine = create_engine(
            f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}",
            echo=echo,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator:
        """Контекстный менеджер возвращает новый Session и гарантированно закрывает его."""
        session = self.SessionLocal()
        try:
            with allure.step("get DB session"):
                yield session
        finally:
            session.close()



