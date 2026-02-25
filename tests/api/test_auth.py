"""
Тесты для эндпоинта аутентификации (Auth API).
Регистрация, логин и негативные сценарии.
"""
from datetime import datetime

import allure
import pytest
from pytest_check import check

from api.api_manager import ApiManager
from entities.user import User
from enums.roles import Roles
from models.base_models import LoginResponse, UserPayload, RegisterUserResponse

pytestmark = pytest.mark.api


class TestAuthApi:
    """Позитивные и негативные проверки Auth API (register, login)."""

    # --- POST /register ---

    @pytest.mark.slow
    def test_register_user(self, api_manager: ApiManager, fresh_user: UserPayload) -> None:
        """Позитив: регистрация пользователя с данными из фикстуры — 201, в ответе email, id, roles."""
        response = api_manager.auth_api.register_user(fresh_user)
        register_user_response = RegisterUserResponse(**response.json())

        assert register_user_response.email == fresh_user.email, "Email не совпадает"

    # --- POST /login ---

    @pytest.mark.slow
    def test_auth_user_success(self, api_manager: ApiManager, login_data: dict) -> None:
        """Позитив: логин с валидными кредами — 200, в ответе accessToken и user.email."""
        response = api_manager.auth_api.login_user(login_data)
        login_response = LoginResponse(**response.json())

        assert login_response.user.email == login_data["email"]

    def test_auth_user_fail_password_is_not_true(self, api_manager: ApiManager, login_data: dict) -> None:
        """Негатив: логин с неверным паролем — 401, сообщение об ошибке."""
        wrong_login = {**login_data, "password": "pass"}
        response = api_manager.auth_api.login_user(wrong_login, expected_status=401)

        assert response.json().get("message") == "Неверный логин или пароль"

    def test_auth_user_fail_email_is_not_exist(self, api_manager: ApiManager, login_data: dict) -> None:
        """Негатив: логин с несуществующим email — 401, сообщение об ошибке."""
        wrong_login = {**login_data, "email": login_data["email"] + "wrong"}
        response = api_manager.auth_api.login_user(wrong_login, expected_status=401)

        assert response.json().get("message") == "Неверный логин или пароль"

    def test_auth_user_fail_body_is_empty(self, api_manager: ApiManager) -> None:
        """Негатив: логин с пустым телом — 401, сообщение об ошибке."""
        response = api_manager.auth_api.login_user({}, expected_status=401)

        assert response.json().get("message") == "Неверный логин или пароль"

    @allure.title("Тест регистрации пользователя с помощью Mock")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "Viktor")
    def test_register_user_mock(self, api_manager: ApiManager, test_user: UserPayload, mocker):
        with allure.step(" Мокаем метод register_user в auth_api"):
            mock_response = RegisterUserResponse(  # Фиктивный ответ
                id="id",
                email="email@email.com",
                fullName="INCORRECT_NAME",
                verified=True,
                banned=False,
                roles=[Roles.SUPER_ADMIN],
                createdAt=str(datetime.now())
            )

            mocker.patch.object(
                api_manager.auth_api,  # Объект, который нужно замокать
                'register_user',  # Метод, который нужно замокать
                return_value=mock_response  # Фиктивный ответ
            )

        with allure.step("Вызываем метод, который должен быть замокан"):
            register_user_response = api_manager.auth_api.register_user(test_user)

        with allure.step("Проверяем, что ответ соответствует ожидаемому"):
            with allure.step("Проверка поля персональных данных"):
                with check:
                    check.equal(register_user_response.fullName, "INCORRECT_NAME", "НЕСОВПАДЕНИЕ fullName")
                    check.equal(register_user_response.email, mock_response.email)

            with allure.step("Проверка поля banned"):
                with check("Проверка поля banned"):  # можно использовать вместо allure.step
                    check.equal(register_user_response.banned, mock_response.banned)
