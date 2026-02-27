"""
Клиент Auth API: регистрация, логин, установка Bearer в сессию.
"""
import requests

from constants.constants import AUTH_BASE_URL, REGISTER_ENDPOINT, LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from models.base_models import LoginPayload, UserPayload


class AuthAPI(CustomRequester):
    """
    Работа с эндпоинтами аутентификации (register, login).
    Использует AUTH_BASE_URL.
    """

    def __init__(self, session: requests.Session) -> None:
        """
        :param session: HTTP-сессия для запросов (общая с другими API при использовании ApiManager).
        """
        super().__init__(session, base_url=AUTH_BASE_URL)

    def register_user(self, user_data: UserPayload, expected_status: int = 201) -> requests.Response:
        """
        POST /register — регистрация нового пользователя.
        :param user_data: Модель UserPayload (email, fullName, password, passwordRepeat, roles).
        :param expected_status: Ожидаемый HTTP-статус (по умолчанию 201).
        :return: requests.Response.
        """
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=user_data,
            expected_status=expected_status
        )

    def login_user(
        self, login_data: LoginPayload | None, expected_status: int = 201
    ) -> requests.Response:
        """
        POST /login — авторизация, возвращает accessToken и user в теле ответа.
        :param login_data: Модель LoginPayload (email, password) или None для пустого тела.
        :param expected_status: Ожидаемый HTTP-статус (по умолчанию 201).
        :return: requests.Response.
        """
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data={} if login_data is None else login_data,
            expected_status=expected_status
        )

    def authenticate(self, email: str, password: str) -> None:
        """
        Выполняет логин и записывает Bearer-токен в заголовки сессии.
        Дальнейшие запросы через эту сессию идут с авторизацией.
        :param email: Email пользователя.
        :param password: Пароль.
        :raises KeyError: Если в ответе нет accessToken.
        """
        login_data = LoginPayload(email=email, password=password)
        response = self.login_user(login_data).json()
        if "accessToken" not in response:
            raise KeyError("token is missing")

        token = response["accessToken"]
        self._update_session_headers({"authorization": "Bearer " + token})