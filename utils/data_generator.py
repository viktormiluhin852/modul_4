"""
Генерация случайных тестовых данных: пользователи (email, имя, пароль), фильмы (название, описание, цена и т.д.).
"""
import random
import string
import uuid
from faker import Faker
from constants import MOVIE_GENRE_IDS

faker = Faker()


class DataGenerator:
    """
    Статические методы для генерации полей при создании пользователей и фильмов в тестах.
    Уникальные значения уменьшают коллизии при повторных запусках.
    """

    @staticmethod
    def generate_random_email() -> str:
        """Случайный email вида kek<8 символов>@gmail.com."""
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"

    @staticmethod
    def generate_random_name() -> str:
        """Случайное имя и фамилия (Faker)."""
        return f"{faker.first_name()} {faker.last_name()}"

    @staticmethod
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
    def generate_random_movie_name() -> str:
        """Уникальное название фильма (чтобы избежать 409 при повторном создании)."""
        return f"Фильм {faker.word()} {uuid.uuid4().hex[:8]}"

    @staticmethod
    def generate_random_movie_description() -> str:
        """Случайное описание фильма."""
        return faker.text(max_nb_chars=200)

    @staticmethod
    def generate_random_movie_price() -> int:
        """Случайная цена фильма."""
        return random.randint(100, 1000)

    @staticmethod
    def generate_random_movie_location() -> str:
        """Случайный город: MSK или SPB."""
        return random.choice(["MSK", "SPB"])

    @staticmethod
    def generate_random_movie_image_url() -> str:
        """Случайный URL картинки для фильма."""
        return f"https://image.example.com/{uuid.uuid4().hex}.jpg"

    @staticmethod
    def generate_random_movie_published() -> bool:
        """Случайное значение published (опубликован/черновик)."""
        return random.choice([True, False])

    @staticmethod
    def generate_random_movie_genre_id() -> int:
        """Случайный id жанра из списка существующих (GET /genres)."""
        return random.choice(MOVIE_GENRE_IDS)





