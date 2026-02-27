"""
Клиент Movies API: список фильмов, CRUD по фильму (хост api.dev-cinescope).
"""
from typing import Optional

import requests
import allure

from constants.constants import BASE_URL, MOVIES_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from models.base_models import GetMoviesParams, MoviePatchPayload, MoviePayload


class MoviesAPI(CustomRequester):
    """
    Работа с эндпоинтами /movies: получение списка, по id, создание, редактирование, удаление.
    POST/PATCH/DELETE требуют роль SUPER_ADMIN (Bearer в сессии).
    """

    def __init__(self, session: requests.Session, base_url: str = BASE_URL) -> None:
        """
        :param session: HTTP-сессия; для записи/удаления нужен Bearer.
        :param base_url: Базовый URL Movies API (по умолчанию из constants).
        """
        super().__init__(session, base_url=base_url)

    @allure.step("GET /movies — получение списка (params={params})")
    def get_movies(
        self,
        params: Optional[GetMoviesParams] = None,
        expected_status: int = 200,
    ) -> requests.Response:
        """
        GET /movies — список афиш с пагинацией и фильтрами.
        :param params: Опциональные query: pageSize, page, minPrice, maxPrice, locations, published, genreId, createdAt.
        :param expected_status: Ожидаемый HTTP-статус (по умолчанию 200).
        :return: requests.Response.
        """
        return self.send_request(
            method="GET",
            endpoint=MOVIES_ENDPOINT,
            params=params,
            expected_status=expected_status
        )

    @allure.step("GET /movies/{movie_id} — получение фильма")
    def get_movie(self, movie_id: int, expected_status: int = 200) -> requests.Response:
        """
        GET /movies/{id} — получение одного фильма (в т.ч. отзывы).
        :param movie_id: Идентификатор фильма.
        :param expected_status: Ожидаемый HTTP-статус (по умолчанию 200).
        :return: requests.Response.
        """
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            expected_status=expected_status,
        )

    @allure.step("POST /movies — создание фильма")
    def create_movie(
        self,
        data: MoviePayload | MoviePatchPayload,
        expected_status: int = 201,
    ) -> requests.Response:
        """
        POST /movies — создание фильма. Требуется SUPER_ADMIN.
        :param data: Модель MoviePayload или MoviePatchPayload (для негативных тестов с неполным телом).
        :param expected_status: Ожидаемый HTTP-статус (по умолчанию 201).
        :return: requests.Response.
        """
        return self.send_request(
            method="POST",
            endpoint=MOVIES_ENDPOINT,
            data=data,
            expected_status=expected_status,
        )

    @allure.step("PATCH /movies/{movie_id} — редактирование фильма")
    def edit_movie(
        self, movie_id: int, data: MoviePatchPayload, expected_status: int = 200
    ) -> requests.Response:
        """
        PATCH /movies/{id} — редактирование фильма. Требуется SUPER_ADMIN.
        :param movie_id: Идентификатор фильма.
        :param data: Модель MoviePatchPayload (все поля опциональны).
        :param expected_status: Ожидаемый HTTP-статус (по умолчанию 200).
        :return: requests.Response.
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            data=data,
            expected_status=expected_status,
        )

    @allure.step("DELETE /movies/{movie_id} — удаление фильма")
    def delete_movie(self, movie_id: int, expected_status: int = 200) -> requests.Response:
        """
        DELETE /movies/{id} — удаление фильма. Требуется SUPER_ADMIN.
        :param movie_id: Идентификатор фильма.
        :param expected_status: Ожидаемый HTTP-статус (по умолчанию 200).
        :return: requests.Response.
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            expected_status=expected_status,
        )
