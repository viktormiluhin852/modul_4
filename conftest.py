"""
Фикстуры pytest: пользователи (test_user, fresh_user, registered_user), сессия, api_manager,
админ-сессия для Movies, данные фильма и созданный фильм с очисткой.
"""
from typing import Generator, Callable, Any

import pytest
import requests
from faker import Faker

from sqlalchemy.orm import Session

from db_models.user import UserDBModel
from db_requester.db_client import get_db_session

from api.api_manager import ApiManager
from enums.roles import Roles
from entities.user import User
from models.base_models import UserPayload, MoviePayload, MovieResponse
from resources.user_creds import SuperAdminCreds
from utils.data_generator import DataGenerator
from db_requester.db_helpers import DBHelper
from services.movie_service import MovieService

faker = Faker()


@pytest.fixture(scope="session")
def test_user() -> UserPayload:
    """
    Один пользователь на всю сессию: для тестов логина.
    """
    random_password = DataGenerator.generate_random_password()

    return UserPayload(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER]
    )


@pytest.fixture(scope="function")
def fresh_user() -> UserPayload:
    """
    Данные нового пользователя на каждый тест (для test_register_user).
    Генерируются заново при каждом запросе фикстуры.
    """
    password = DataGenerator.generate_random_password()
    return UserPayload(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=password,
        passwordRepeat=password,
        roles=[Roles.USER]
    )


@pytest.fixture(scope="session")
def registered_user(api_manager: ApiManager, test_user: UserPayload) -> Generator[UserPayload, None, None]:
    """
    Регистрирует test_user один раз за сессию, отдаёт данные для тестов.
    После всех тестов удаляет пользователя через UserAPI.delete_user.
    """
    response = api_manager.auth_api.register_user(test_user)
    response_data = response.json()
    user = test_user.model_copy()
    user.id = response_data.get("id")

    yield user

    api_manager.auth_api.authenticate(user.email, user.password)
    api_manager.user_api.delete_user(user.id)


@pytest.fixture
def login_data(registered_user: UserPayload) -> dict:
    """Тело запроса для POST /login: email и password зарегистрированного пользователя."""
    return {
        "email": registered_user.email,
        "password": registered_user.password,
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


@pytest.fixture(scope="function")
def movie_data() -> MoviePayload:
    """
    Данные фильма для создания (как test_user для auth).
    Собирается из отдельных генераторов полей.
    """
    return MoviePayload(
        name=DataGenerator.generate_random_movie_name(),
        price=DataGenerator.generate_random_movie_price(),
        description=DataGenerator.generate_random_movie_description(),
        imageUrl=DataGenerator.generate_random_movie_image_url(),
        location=DataGenerator.generate_random_movie_location(),
        published=DataGenerator.generate_random_movie_published(),
        genreId=DataGenerator.generate_random_movie_genre_id(),
    )


@pytest.fixture
def created_movie(super_admin: User, movie_data: MoviePayload) -> Generator[MovieResponse, None, None]:
    """
    Создаёт фильм через POST /movies от имени SUPER_ADMIN, отдаёт модель ответа.
    В teardown удаляет фильм через DELETE /movies/{id}.
    """
    response = super_admin.api.movies_api.create_movie(movie_data.model_dump())
    movie = MovieResponse(**response.json())

    yield movie

    super_admin.api.movies_api.delete_movie(movie.id)

@pytest.fixture(scope="session")
def user_session() -> Generator[Callable[[], ApiManager], None, None]:
    user_pool = []

    def _create_user_session() -> ApiManager:
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture(scope="session")
def super_admin(user_session: Callable[[], ApiManager]) -> User:
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        list(Roles.SUPER_ADMIN.value),
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds[0], super_admin.creds[1])
    return super_admin

@pytest.fixture
def admin_user(
    user_session: Callable[[], ApiManager],
    super_admin: User,
    creation_user_data: UserPayload,
) -> User:
    """Пользователь с ролью ADMIN: создаётся через super_admin, логинится в своей сессии."""
    new_session = user_session()
    admin_user = User(
        creation_user_data.email,
        creation_user_data.password,
        list(Roles.ADMIN.value),
        new_session,
    )
    super_admin.api.user_api.create_user(creation_user_data)
    admin_user.api.auth_api.authenticate(admin_user.creds[0], admin_user.creds[1])
    return admin_user

@pytest.fixture
def common_user(
    user_session: Callable[[], ApiManager],
    super_admin: User,
    creation_user_data: UserPayload,
) -> User:
    """Пользователь с ролью USER: создаётся через super_admin, логинится в своей сессии."""
    new_session = user_session()
    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        list(Roles.USER.value),
        new_session,
    )
    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds[0], common_user.creds[1])
    return common_user


@pytest.fixture(scope="function")
def creation_user_data(fresh_user: UserPayload) -> UserPayload:
    """Данные для создания пользователя с ролью USER (verified, banned)."""
    updated_data = fresh_user.model_copy()
    updated_data.verified = True
    updated_data.banned = False
    return updated_data

@pytest.fixture(scope="module")
def db_session() -> Generator[Session, None, None]:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    yield db_session
    db_session.close()

@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    """Репозиторий для работы с БД в тестах."""
    return DBHelper(db_session)


@pytest.fixture(scope="function")
def movie_service(db_helper: DBHelper) -> MovieService:
    """Сервис фильмов: маппер + репозиторий. Принимает модель, пишет в БД."""
    return MovieService(db_helper)

@pytest.fixture(scope="function")
def created_test_user(db_helper) -> Generator[UserDBModel, None, None]:
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user
    # Cleanup после теста
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)


