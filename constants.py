"""
Константы проекта: базовые URL API, эндпоинты, заголовки, креды.
"""
from typing import Dict, List

# Auth API
AUTH_BASE_URL: str = "https://auth.dev-cinescope.coconutqa.ru/"
LOGIN_ENDPOINT: str = "/login"
REGISTER_ENDPOINT: str = "/register"
USER_ENDPOINT: str = "/user"

# API Movies (тот же хост/подход — одна база)
BASE_URL: str = "https://api.dev-cinescope.coconutqa.ru/"
MOVIES_ENDPOINT: str = "/movies"
# ID жанров из GET /genres (основные 1–10)
MOVIE_GENRE_IDS: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

HEADERS: Dict[str, str] = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Креды админа для API Movies (все роли, в т.ч. SUPER_ADMIN)
ADMIN_EMAIL: str = "api1@gmail.com"
ADMIN_PASSWORD: str = "asdqwe123Q"

