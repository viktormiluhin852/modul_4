"""
Константы проекта: базовые URL API, эндпоинты, заголовки, креды.
"""
# Auth API
AUTH_BASE_URL = "https://auth.dev-cinescope.coconutqa.ru/"
LOGIN_ENDPOINT = "/login"
REGISTER_ENDPOINT = "/register"
USER_ENDPOINT = "/user"

# API Movies (тот же хост/подход — одна база)
BASE_URL = "https://api.dev-cinescope.coconutqa.ru/"
MOVIES_ENDPOINT = "/movies"
# ID жанров из GET /genres (основные 1–10)
MOVIE_GENRE_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Креды админа для API Movies (все роли, в т.ч. SUPER_ADMIN)
ADMIN_EMAIL = "api1@gmail.com"
ADMIN_PASSWORD = "asdqwe123Q"

