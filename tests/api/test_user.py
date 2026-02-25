import pytest

from entities.user import User
from models.base_models import UserPayload, RegisterUserResponse

pytestmark = pytest.mark.api


class TestUser:
    def test_create_user(self, super_admin: User, creation_user_data: UserPayload):
        response = super_admin.api.user_api.create_user(creation_user_data)
        register_user_response = RegisterUserResponse(**response.json())

        assert register_user_response.id != '', "ID должен быть не пустым"
        assert register_user_response.email == creation_user_data.email
        assert register_user_response.fullName == creation_user_data.fullName
        assert register_user_response.roles == creation_user_data.roles
        assert register_user_response.verified is True

    @pytest.mark.slow
    def test_get_user_by_locator(self, super_admin: User, creation_user_data: UserPayload):
        created_user = RegisterUserResponse(**super_admin.api.user_api.create_user(creation_user_data).json())
        user_by_id = RegisterUserResponse(**super_admin.api.user_api.get_user_info(created_user.id).json())
        user_by_email = RegisterUserResponse(**super_admin.api.user_api.get_user_info(created_user.email).json())

        assert user_by_id == user_by_email, "Содержание ответов должно быть идентичным"
        assert user_by_id.id != '', "ID должен быть не пустым"
        assert user_by_id.email == creation_user_data.email
        assert user_by_id.fullName == creation_user_data.fullName
        assert user_by_id.roles[0] == creation_user_data.roles[0]
        assert user_by_id.verified is True

    def test_get_user_by_id_common_user(self, common_user : User):
        common_user.api.user_api.get_user_info(common_user.email, expected_status=403)

