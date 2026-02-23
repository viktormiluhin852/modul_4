"""
Фикстуры pytest: пользователи (test_user, fresh_user, registered_user), сессия, api_manager,
админ-сессия для Movies, данные фильма и созданный фильм с очисткой.
"""
from typing import Any, Dict, Generator

import pytest
import requests
from faker import Faker

from api.api_manager import ApiManager
from constants import ADMIN_EMAIL, ADMIN_PASSWORD, HEADERS, LOGIN_ENDPOINT, REGISTER_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator

faker = Faker()


@pytest.fixture(scope="session")
def test_user() -> Dict[str, Any]:
    """
    Один пользователь на всю сессию: для тестов логина.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"],
    }


@pytest.fixture(scope="function")
def fresh_user() -> Dict[str, Any]:
    """
    Данные нового пользователя на каждый тест (для test_register_user).
    Генерируются заново при каждом запросе фикстуры.
    """
    password = DataGenerator.generate_random_password()
    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": password,
        "passwordRepeat": password,
        "roles": ["USER"],
    }


@pytest.fixture(scope="session")
def registered_user(api_manager: ApiManager, test_user: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Регистрирует test_user один раз за сессию, отдаёт данные для тестов.
    После всех тестов удаляет пользователя через UserAPI.delete_user.
    """
    response = api_manager.auth_api.register_user(test_user)
    response_data = response.json()
    user = test_user.copy()
    user["id"] = response_data.get("id")

    yield user

    api_manager.auth_api.authenticate(user["email"], user["password"])
    api_manager.user_api.delete_user(user["id"])


@pytest.fixture
def login_data(registered_user: Dict[str, Any]) -> Dict[str, str]:
    """Тело запроса для POST /login: email и password зарегистрированного пользователя."""
    return {
        "email": registered_user["email"],
        "password": registered_user["password"],
    }

@pytest.fixture(scope="session")
def session() -> Generator[requests.Session, None, None]:
    """
    Одна HTTP-сессия на всю тестовую сессию; в конце закрывается.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session: requests.Session) -> ApiManager:
    """
    ApiManager с общей сессией; создаёт auth_api, user_api, movies_api.
    """
    return ApiManager(session)


@pytest.fixture(scope="session")
def api_manager_admin(api_manager: ApiManager) -> ApiManager:
    """
    ApiManager с залогиненным админом (Bearer в сессии).
    Используется для тестов Movies API (POST/PATCH/DELETE требуют SUPER_ADMIN).
    """
    api_manager.auth_api.authenticate(ADMIN_EMAIL, ADMIN_PASSWORD)
    return api_manager


@pytest.fixture(scope="function")
def movie_data() -> Dict[str, Any]:
    """
    Данные фильма для создания (как test_user для auth).
    Собирается из отдельных генераторов полей.
    """
    return {
        "name": DataGenerator.generate_random_movie_name(),
        "price": DataGenerator.generate_random_movie_price(),
        "description": DataGenerator.generate_random_movie_description(),
        "imageUrl": DataGenerator.generate_random_movie_image_url(),
        "location": DataGenerator.generate_random_movie_location(),
        "published": DataGenerator.generate_random_movie_published(),
        "genreId": DataGenerator.generate_random_movie_genre_id(),
    }


@pytest.fixture
def created_movie(api_manager_admin: ApiManager, movie_data: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """
    Создаёт фильм через POST /movies, отдаёт копию movie_data с полем id.
    В teardown удаляет фильм через DELETE /movies/{id}.
    """
    response = api_manager_admin.movies_api.create_movie(movie_data)
    response_data = response.json()
    movie = movie_data.copy()
    movie["id"] = response_data.get("id")

    yield movie

    api_manager_admin.movies_api.delete_movie(movie["id"])