from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.orm import declarative_base
from typing import Dict, Any

Base = declarative_base()

# Тип Location уже есть в БД (public."Location"), не создаём заново
location_enum = PG_ENUM("MSK", "SPB", name="Location", schema="public", create_type=False)


class MovieDBModel(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True)  # serial4 в БД
    name = Column(String)  # text в БД
    price = Column(Integer)  # int4 в БД
    description = Column(String)  # text в БД
    image_url = Column(String)  # text в БД
    location = Column(location_enum)  # public."Location" (enum) в БД
    published = Column(Boolean)  # bool в БД
    rating = Column(Float)  # float8 в БД
    genre_id = Column(Integer)  # int4 в БД
    created_at = Column(DateTime)  # timestamp в БД

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь."""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "image_url": self.image_url,
            "location": self.location,
            "published": self.published,
            "rating": self.rating,
            "genre_id": self.genre_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<Movie(id={self.id}, name='{self.name}')>"
