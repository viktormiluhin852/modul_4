"""
Клиент Movies API: список фильмов, CRUD по фильму (хост api.dev-cinescope).
"""
from typing import Any, Dict, Optional

import requests

from constants import BASE_URL, MOVIES_ENDPOINT
from custom_requester.custom_requester import CustomRequester


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

    def get_movies(self, params: Optional[Dict[str, Any]] = None, expected_status: int = 200) -> requests.Response:
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
            expected_status=expected_status,
        )

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

    def create_movie(self, data: Dict[str, Any], expected_status: int = 201) -> requests.Response:
        """
        POST /movies — создание фильма. Требуется SUPER_ADMIN.
        :param data: Словарь: name, price, description, imageUrl, location, published, genreId.
        :param expected_status: Ожидаемый HTTP-статус (по умолчанию 201).
        :return: requests.Response.
        """
        return self.send_request(
            method="POST",
            endpoint=MOVIES_ENDPOINT,
            data=data,
            expected_status=expected_status,
        )

    def edit_movie(self, movie_id: int, data: Dict[str, Any], expected_status: int = 200) -> requests.Response:
        """
        PATCH /movies/{id} — редактирование фильма. Требуется SUPER_ADMIN.
        :param movie_id: Идентификатор фильма.
        :param data: Поля для обновления (name, description, price, location, imageUrl, published, genreId).
        :param expected_status: Ожидаемый HTTP-статус (по умолчанию 200).
        :return: requests.Response.
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            data=data,
            expected_status=expected_status,
        )

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
