from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.orm import declarative_base, DeclarativeMeta
from typing import Dict, Any
from models.base_models import MovieResponse
from datetime import datetime, timezone
import allure

Base: DeclarativeMeta = declarative_base()

# Тип Location уже есть в БД (public."Location"), не создаём заново
location_enum = PG_ENUM("MSK", "SPB", name="Location", schema="public", create_type=False)


class MovieDBModel(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    price = Column(Integer)
    description = Column(String)
    image_url = Column(String)
    location = Column(location_enum)
    published = Column(Boolean)
    rating = Column(Float)
    genre_id = Column(Integer)
    created_at = Column(DateTime)

    @allure.step("to_model MovieDBModel")
    def to_model(self) -> MovieResponse:
        """Преобразование в Pydantic модель MovieResponse."""
        data = {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "image_url": self.image_url,
            "location": self.location,
            "published": self.published,
            "rating": self.rating,
            "genre_id": self.genre_id,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
        return MovieResponse(**data)

    def __repr__(self) -> str:
        return f"<Movie(id={self.id}, name='{self.name}')>"

    @classmethod
    @allure.step("from_payload MovieDBModel")
    def from_payload(cls, payload) -> "MovieDBModel":
        """Создать экземпляр MovieDBModel из MoviePayload (не коммитит)."""
        data = payload.model_dump(by_alias=True, exclude_none=True)
        data.setdefault("rating", 0.0)
        data.setdefault("created_at", datetime.now(timezone.utc))
        return cls(**data)
