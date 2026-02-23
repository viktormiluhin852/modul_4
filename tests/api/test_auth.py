"""
Тесты для эндпоинта аутентификации (Auth API).
Регистрация, логин и негативные сценарии.
"""


class TestAuthApi:
    """Позитивные и негативные проверки Auth API (register, login)."""

    # --- POST /register ---

    def test_register_user(self, api_manager, fresh_user):
        """Позитив: регистрация пользователя с данными из фикстуры — 201, в ответе email, id, roles."""
        response = api_manager.auth_api.register_user(fresh_user)
        response_data = response.json()

        assert response_data["email"] == fresh_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    # --- POST /login ---

    def test_auth_user_success(self, api_manager, login_data):
        """Позитив: логин с валидными кредами — 200, в ответе accessToken и user.email."""
        response = api_manager.auth_api.login_user(login_data)
        data = response.json()

        assert "accessToken" in data
        assert login_data["email"] == data.get("user", {}).get("email")

    def test_auth_user_fail_password_is_not_true(self, api_manager, login_data):
        """Негатив: логин с неверным паролем — 401, сообщение об ошибке."""
        wrong_login = {**login_data, "password": "pass"}
        response = api_manager.auth_api.login_user(wrong_login, expected_status=401)

        assert response.json().get("message") == "Неверный логин или пароль"

    def test_auth_user_fail_email_is_not_exist(self, api_manager, login_data):
        """Негатив: логин с несуществующим email — 401, сообщение об ошибке."""
        wrong_login = {**login_data, "email": login_data["email"] + "wrong"}
        response = api_manager.auth_api.login_user(wrong_login, expected_status=401)

        assert response.json().get("message") == "Неверный логин или пароль"

    def test_auth_user_fail_body_is_empty(self, api_manager):
        """Негатив: логин с пустым телом — 401, сообщение об ошибке."""
        response = api_manager.auth_api.login_user({}, expected_status=401)

        assert response.json().get("message") == "Неверный логин или пароль"
