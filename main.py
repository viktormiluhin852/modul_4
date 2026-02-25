from pydantic import BaseModel
from venv import logger


class User(BaseModel):  # Создается класс User с помощью BaseModel от pydantic и указывается
    name: str       # что имя должно быть строкой
    age: int        # возраст должен быть числом
    adult: bool     # поле совершенолетие должно быть булевым значением


def get_user() -> dict:  # функция get_user возвращает обьект dict с следущими полями
    return {
        "name": "Alice",
        "age": 25,
        "adult": "true"
    }


def test_user_data() -> None:
    user = User(**get_user())  # Проверяем возможность конвертации данных и соответствия типов данных с помощью Pydantic
    assert user.name == "Alice"  # Возможность дополнительных проверок
    logger.info(f"{user.name=} {user.age=} {user.adult=}")  # а также возможность удобного взаимодействия
