"""Загрузка параметров подключения к базе данных из .env."""

import os
from dotenv import load_dotenv

load_dotenv()


class MoviesDbCreds:
    """Контейнер с параметрами подключения к БД (host, port, database, user, password)."""

    HOST = os.getenv('DB_HOST')
    PORT = os.getenv('DB_PORT')
    DATABASE_NAME = os.getenv('DB_NAME')
    USERNAME = os.getenv('DB_USER')
    PASSWORD = os.getenv('DB_PASS')