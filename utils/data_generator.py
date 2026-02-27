"""
Генерация случайных тестовых данных: пользователи (email, имя, пароль), фильмы (название, описание, цена и т.д.).
"""
import datetime
import random
import string
import uuid
from faker import Faker
from constants.constants import MOVIE_GENRE_IDS
import allure

faker = Faker()


class DataGenerator:
    """
    Статические методы для генерации полей при создании пользователей и фильмов в тестах.
    Уникальные значения уменьшают коллизии при повторных запусках.
    """

    @staticmethod
    @allure.step("generate_random_int {max}")
    def generate_random_int(max: int) -> int:
        return random.randint(1, max)

    @staticmethod
    @allure.step("generate_random_email")
    def generate_random_email() -> str:
        """Случайный email вида kek<8 символов>@gmail.com."""
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"

    @staticmethod
    @allure.step("generate_random_name")
    def generate_random_name() -> str:
        """Случайное имя и фамилия (Faker)."""
        return f"{faker.first_name()} {faker.last_name()}"

    @staticmethod
    @allure.step("generate_random_password")
    def generate_random_password() -> str:
        """
        Генерация пароля, соответствующего требованиям:
        - Минимум 1 буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 8 до 20 символов.
        """

        letters = random.choice(string.ascii_letters)
        digits = random.choice(string.digits)

        special_chars = '?@#$%^&|:'
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18)
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

    @staticmethod
    @allure.step("generate_random_movie_name")
    def generate_random_movie_name() -> str:
        """Уникальное название фильма (чтобы избежать 409 при повторном создании)."""
        return f"Фильм {faker.word()} {uuid.uuid4().hex[:8]}"

    @staticmethod
    @allure.step("generate_random_movie_description")
    def generate_random_movie_description() -> str:
        """Случайное описание фильма."""
        return faker.text(max_nb_chars=200)

    @staticmethod
    @allure.step("generate_random_movie_price")
    def generate_random_movie_price() -> int:
        """Случайная цена фильма."""
        return random.randint(100, 1000)

    @staticmethod
    @allure.step("generate_random_movie_location")
    def generate_random_movie_location() -> str:
        """Случайный город: MSK или SPB."""
        return random.choice(["MSK", "SPB"])

    @staticmethod
    @allure.step("generate_random_movie_image_url")
    def generate_random_movie_image_url() -> str:
        """Случайный URL картинки для фильма."""
        return f"https://image.example.com/{uuid.uuid4().hex}.jpg"

    @staticmethod
    @allure.step("generate_random_movie_published")
    def generate_random_movie_published() -> bool:
        """Случайное значение published (опубликован/черновик)."""
        return random.choice([True, False])

    @staticmethod
    @allure.step("generate_random_movie_genre_id")
    def generate_random_movie_genre_id() -> int:
        """Случайный id жанра из списка существующих (GET /genres)."""
        return random.choice(MOVIE_GENRE_IDS)

    @staticmethod
    @allure.step("generate_user_data")
    def generate_user_data() -> dict:
        """Генерирует данные для тестового пользователя"""
        from uuid import uuid4

        return {
            'id': f'{uuid4()}',  # генерируем UUID как строку
            'email': DataGenerator.generate_random_email(),
            'full_name': DataGenerator.generate_random_name(),
            'password': DataGenerator.generate_random_password(),
            'created_at': datetime.datetime.now(),
            'updated_at': datetime.datetime.now(),
            'verified': False,
            'banned': False,
            'roles': '{USER}'
        }





