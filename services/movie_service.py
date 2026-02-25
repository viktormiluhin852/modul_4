"""
Сервис фильмов: оркестрирует маппинг (payload → dict) и репозиторий (запись в БД)
"""
from db_models.movies import MovieDBModel
from db_requester.db_helpers import DBHelper
from models.base_models import MoviePayload
from utils.db_mappers import movie_payload_to_db_dict


class MovieService:
    def __init__(self, repository: DBHelper) -> None:
        self._repository = repository

    def create_movie(self, payload: MoviePayload) -> MovieDBModel:
        """Создаёт фильм в БД: маппинг payload → dict, затем запись через репозиторий."""
        data = movie_payload_to_db_dict(payload)
        return self._repository.create_test_movie(data)

    def get_movie_by_name(self, name: str) -> MovieDBModel | None:
        """Возвращает фильм по названию или None."""
        return self._repository.get_movie_by_name(name)

    def delete_movie(self, movie: MovieDBModel) -> None:
        """Удаляет фильм из БД."""
        self._repository.cleanup_test_data([movie])
