"""
Сервис фильмов: оркестрирует маппинг (payload → dict) и репозиторий (запись в БД)
"""
from db_models.movies import MovieDBModel
from db_requester.db_helpers import DBHelper
from models.base_models import MoviePayload
import allure


class MovieService:
    def __init__(self, repository: DBHelper) -> None:
        self._repository = repository

    @allure.step("create_movie")
    def create_movie(self, payload: MoviePayload) -> MovieDBModel:
        """Создаёт фильм в БД: маппинг payload → dict, затем запись через репозитория."""
        with allure.step("create_movie"):
            # Передаём модель в репозиторий — он сам выполнит маппинг
            return self._repository.create_test_movie(payload)

    @allure.step("get_movie_by_name")
    def get_movie_by_name(self, name: str) -> MovieDBModel | None:
        """Возвращает фильм по названию или None."""
        with allure.step("get_movie_by_name"):
            return self._repository.get_movie_by_name(name)

    @allure.step("delete_movie")
    def delete_movie(self, movie: MovieDBModel) -> None:
        """Удаляет фильм из БД."""
        with allure.step("delete_movie"):
            self._repository.cleanup_test_data([movie])
