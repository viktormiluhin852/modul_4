from api.api_manager import ApiManager
import allure


class User:
    def __init__(self, email: str, password: str, roles: list, api: ApiManager):
        self.email = email
        self.password = password
        self.roles = roles
        self.api = api  # Сюда будем передавать экземпляр API Manager для запросов

    @property
    @allure.step("get user creds")
    def creds(self):
        """Возвращает кортеж (email, password)"""
        with allure.step("get user creds"):
            return self.email, self.password


