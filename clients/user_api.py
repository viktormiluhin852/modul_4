"""
Клиент User API: получение и удаление пользователей (Auth-хост).
"""
import requests

from constants import AUTH_BASE_URL, USER_ENDPOINT
from custom_requester.custom_requester import CustomRequester


class UserAPI(CustomRequester):
    """
    Работа с эндпоинтами пользователей (GET /user/{id}, DELETE /user/{id}).
    Требует авторизации для удаления (USER может удалить только себя).
    """

    def __init__(self, session: requests.Session) -> None:
        """
        :param session: HTTP-сессия; для DELETE нужен Bearer в заголовках.
        """
        super().__init__(session, base_url=AUTH_BASE_URL)

    def get_user_info(self, user_id: str, expected_status: int = 200) -> requests.Response:
        """
        GET /user/{id} — получение информации о пользователе.
        :param user_id: Идентификатор пользователя (UUID).
        :param expected_status: Ожидаемый HTTP-статус (по умолчанию 200).
        :return: requests.Response.
        """
        return self.send_request(
            method="GET",
            endpoint=f"{USER_ENDPOINT}/{user_id}",
            expected_status=expected_status
        )

    def delete_user(self, user_id: str, expected_status: int = 200) -> requests.Response:
        """
        DELETE /user/{id} — удаление пользователя (USER только себя).
        :param user_id: Идентификатор пользователя (UUID).
        :param expected_status: Ожидаемый HTTP-статус (по умолчанию 200).
        :return: requests.Response.
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"{USER_ENDPOINT}/{user_id}",
            expected_status=expected_status
        )
