"""Маппинг API-моделей (payload) в dict для записи в БД (snake_case)."""
from datetime import datetime, timezone
from typing import Any, Dict

from models.base_models import MoviePayload


def movie_payload_to_db_dict(payload: MoviePayload) -> dict:
    """MoviePayload → dict с полями таблицы movies (snake_case)."""
    data = payload.model_dump()
    return {
        "name": data["name"],
        "price": data["price"],
        "description": data["description"],
        "image_url": data["imageUrl"],
        "location": data["location"],
        "published": data["published"],
        "genre_id": data["genreId"],
        "rating": 0.0,
        "created_at": datetime.now(timezone.utc),
    }
