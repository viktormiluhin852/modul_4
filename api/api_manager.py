"""
Менеджер API: создаёт и хранит экземпляры AuthAPI, UserAPI, MoviesAPI с общей сессией.
"""
import requests

from clients.auth_api import AuthAPI
from clients.user_api import UserAPI
from clients.movies_api import MoviesAPI
from constants.constants import BASE_URL
import allure


class ApiManager:
    """
    Централизованное управление API-клиентами с единой HTTP-сессией.
    Все клиенты используют одну и ту же сессию (в т.ч. общие заголовки и cookies).
    """

    def __init__(self, session: requests.Session) -> None:
        """
        Инициализация менеджера и создание клиентов.
        :param session: HTTP-сессия (requests.Session), общая для auth_api, user_api, movies_api.
        """
        self.session = session
        self.auth_api = AuthAPI(session)
        self.user_api = UserAPI(session)
        self.movies_api = MoviesAPI(session, base_url=BASE_URL)


    @allure.step("close session")
    def close_session(self):
        """Закрывает HTTP-сессию."""
        self.session.close()
