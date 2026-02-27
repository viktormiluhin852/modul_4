from sqlalchemy.orm import Session

from db_models.user import UserDBModel
from db_models.movies import MovieDBModel
from models.base_models import MoviePayload, UserDBCreatePayload
from db_models.movies import MovieDBModel
from db_models.user import UserDBModel
import allure


class DBHelper:
    """Класс с методами для работы с БД в тестах"""
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @allure.step("create_test_user")
    def create_test_user(self, user_data: UserDBCreatePayload) -> UserDBModel:
        """Создает тестового пользователя"""
        with allure.step("create_test_user"):
            user = UserDBModel.from_payload(user_data)
            self.db_session.add(user)
            self.db_session.commit()
            self.db_session.refresh(user)
            return user

    @allure.step("get_user_by_id")
    def get_user_by_id(self, user_id: str):
        """Получает пользователя по ID"""
        with allure.step("get_user_by_id"):
            return self.db_session.query(UserDBModel).filter(UserDBModel.id == user_id).first()

    @allure.step("get_user_by_email")
    def get_user_by_email(self, email: str):
        """Получает пользователя по email"""
        with allure.step("get_user_by_email"):
            return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).first()

    @allure.step("create_test_movie")
    def create_test_movie(self, payload: MoviePayload) -> MovieDBModel:
        """Создаёт тестовый фильм в БД. Принимает MoviePayload."""
        with allure.step("create_test_movie"):
            movie = MovieDBModel.from_payload(payload)
            self.db_session.add(movie)
            self.db_session.commit()
            self.db_session.refresh(movie)
            return movie

    @allure.step("get_movie_by_name")
    def get_movie_by_name(self, name: str):
        """Получает фильм по названию"""
        with allure.step("get_movie_by_name"):
            return self.db_session.query(MovieDBModel).filter(MovieDBModel.name == name).first()

    @allure.step("user_exists_by_email")
    def user_exists_by_email(self, email: str) -> bool:
        """Проверяет существование пользователя по email"""
        with allure.step("user_exists_by_email"):
            return self.db_session.query(UserDBModel).filter(UserDBModel.email == email).count() > 0

    @allure.step("delete_user")
    def delete_user(self, user: UserDBModel):
        """Удаляет пользователя"""
        with allure.step("delete_user"):
            self.db_session.delete(user)
            self.db_session.commit()

    @allure.step("cleanup_test_data")
    def cleanup_test_data(self, objects_to_delete: list):
        """Очищает тестовые данные"""
        with allure.step("cleanup_test_data"):
            for obj in objects_to_delete:
                if obj:
                    self.db_session.delete(obj)
            self.db_session.commit()
