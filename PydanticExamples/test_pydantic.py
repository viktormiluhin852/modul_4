# CinescopeFork\Modul_4\PydanticExamples\test_pydantic.py
import pytest
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional
from venv import logger

class PostgresClient:  # Mock - заглушка вмето реального сервиса. делающего запрос в базу данных
    @staticmethod
    def get(key: str):  # Всегда возвращает None
        return None

class Card(BaseModel):
    pan: str = Field(..., min_length=16, max_length=16, description="Номер карты")
    cvc: str = Field(...,  min_length=3, max_length=3)

    @field_validator("pan")  # кастомный валидатор для проверки поля pan
    def check_pan(cls, value: str) -> str:
        """
            не самый лучший пример. не стоит добавлять в валидаторы сложновесную логику
            но данным приером хочется показать что кастомные валидаторы лучше использоват
            для ситуаций которые невозможно проверить доступной логикой Field
        """
        # Проверяем, существует ли карта в Redis
        if PostgresClient.get(f'card_by_pan_{value}') is None:
            raise ValueError("Такой карты не существует")
        return value

@pytest.mark.skip
def test_field_validator():
# Попытка создать объект с данными. отсутствующими в базе данных
    try:
        card = Card(pan="1111222233334444", cvc="123")
        logger.info(card)
    except ValidationError as e:
        logger.info(f"Ошибка валидации: {e}")
        raise