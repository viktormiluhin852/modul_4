import allure
import pytest
from pytest_check import check

from entities.user import User
from models.base_models import UserPayload, RegisterUserResponse

pytestmark = [pytest.mark.api, pytest.mark.regression]


@allure.label("qa_name", "Viktor")
class TestUser:
    @allure.title("Создание пользователя (SUPER_ADMIN)")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.user_smoke
    @pytest.mark.smoke
    def test_create_user(self, super_admin: User, creation_user_data: UserPayload):
        """Позитив: создание пользователя от SUPER_ADMIN — проверка полей ответа (id, email, fullName, roles, verified)."""
        with allure.step("POST /user — создание пользователя (SUPER_ADMIN)"):
            response = super_admin.api.user_api.create_user(creation_user_data)
            register_user_response = RegisterUserResponse(**response.json())

        with allure.step("Проверка полей созданного пользователя"):
            with check:
                check.not_equal(register_user_response.id, '', "ID должен быть не пустым")
                check.equal(register_user_response.email, creation_user_data.email)
                check.equal(register_user_response.fullName, creation_user_data.fullName)
                check.equal(register_user_response.roles, creation_user_data.roles)
                check.equal(register_user_response.verified, True)

    @allure.title("Получение пользователя по id и email")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    def test_get_user_by_locator(self, super_admin: User, creation_user_data: UserPayload):
        """Позитив: получение пользователя по id и по email возвращает идентичные данные."""
        with allure.step("POST /user — создание пользователя"):
            created_user = RegisterUserResponse(**super_admin.api.user_api.create_user(creation_user_data).json())

        with allure.step("GET /user/{id} и GET /user/{email} — получение по id и email"):
            user_by_id = RegisterUserResponse(**super_admin.api.user_api.get_user_info(created_user.id).json())
            user_by_email = RegisterUserResponse(**super_admin.api.user_api.get_user_info(created_user.email).json())

        with allure.step("Проверка: ответы по id и email идентичны"):
            with check:
                check.equal(user_by_id, user_by_email, "Содержание ответов должно быть идентичным")
                check.not_equal(user_by_id.id, '', "ID должен быть не пустым")
                check.equal(user_by_id.email, creation_user_data.email)
                check.equal(user_by_id.fullName, creation_user_data.fullName)
                check.equal(user_by_id.roles[0], creation_user_data.roles[0])
                check.equal(user_by_id.verified, True)

    @allure.title("GET /user/{email} от common_user — 403 Forbidden")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_user_by_id_common_user(self, common_user: User):
        """Негатив: common_user не может получить информацию о пользователе — 403."""
        with allure.step("GET /user/{email} от common_user — ожидаем 403 Forbidden"):
            common_user.api.user_api.get_user_info(common_user.email, expected_status=403)

