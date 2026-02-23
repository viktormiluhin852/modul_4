"""
Тесты для эндпоинта /movies (API Movies).
Используются креды админа для операций, требующих SUPER_ADMIN.
"""
import pytest
from utils.data_generator import DataGenerator


class TestMoviesApi:
    """Позитивные и негативные проверки API Movies."""

    # --- GET /movies ---

    def test_get_movies_success(self, api_manager):
        """Позитив: получение списка фильмов возвращает 200 и корректную структуру."""
        response = api_manager.movies_api.get_movies()
        data = response.json()

        assert "movies" in data
        assert "count" in data
        assert "page" in data
        assert "pageSize" in data
        assert "pageCount" in data
        assert isinstance(data["movies"], list)

    def test_get_movies_with_filters_page_size(self, api_manager):
        """Позитив: фильтр pageSize ограничивает количество записей на странице."""
        page_size = 3
        response = api_manager.movies_api.get_movies(params={"pageSize": page_size})
        data = response.json()

        assert data["pageSize"] == page_size
        assert len(data["movies"]) <= page_size

    def test_get_movies_with_filters_min_max_price(self, api_manager):
        """Позитив: фильтры minPrice и maxPrice сужают выборку по цене."""
        response = api_manager.movies_api.get_movies(
            params={"minPrice": 100, "maxPrice": 500}
        )
        data = response.json()

        for movie in data["movies"]:
            assert 100 <= movie["price"] <= 500

    def test_get_movies_with_filter_locations(self, api_manager):
        """Позитив: фильтр locations (массив MSK/SPB) возвращает только подходящие фильмы."""
        response = api_manager.movies_api.get_movies(params={"locations": ["MSK"]})
        data = response.json()

        for movie in data["movies"]:
            assert movie["location"] == "MSK"

    def test_get_movies_invalid_params_400(self, api_manager):
        """Негатив: неверные параметры (pageSize вне 1–20) — 400."""
        response = api_manager.movies_api.get_movies(
            params={"pageSize": 0},
            expected_status=400,
        )
        assert response.status_code == 400

    # --- GET /movies/{id} ---

    def test_get_movie_by_id_success(self, created_movie, api_manager):
        """Позитив: получение фильма по id возвращает 200 и данные фильма."""
        movie_id = created_movie["id"]
        response = api_manager.movies_api.get_movie(movie_id)
        data = response.json()

        assert data["id"] == movie_id
        assert "name" in data
        assert "price" in data
        assert "description" in data
        assert "location" in data
        assert "reviews" in data

    def test_get_movie_not_found_404(self, api_manager):
        """Негатив: запрос по несуществующему id — 404."""
        response = api_manager.movies_api.get_movie(99999999, expected_status=404)
        assert response.status_code == 404
        assert "Фильм не найден" in response.json().get("message", "")

    # --- POST /movies ---

    def test_create_movie_success(self, api_manager_admin, movie_data):
        """Позитив: создание фильма с данными из фикстуры — 201."""
        response = api_manager_admin.movies_api.create_movie(movie_data)
        data = response.json()

        assert data["name"] == movie_data["name"]
        assert data["price"] == movie_data["price"]
        assert data["description"] == movie_data["description"]
        assert data["location"] == movie_data["location"]
        assert "id" in data

        api_manager_admin.movies_api.delete_movie(data["id"])

    def test_create_movie_duplicate_name_409(self, api_manager_admin, created_movie):
        """Негатив: создание фильма с уже существующим названием — 409."""
        duplicate_data = {
            "name": created_movie["name"],
            "price": DataGenerator.generate_random_movie_price(),
            "description": DataGenerator.generate_random_movie_description(),
            "location": DataGenerator.generate_random_movie_location(),
            "imageUrl": DataGenerator.generate_random_movie_image_url(),
            "published": DataGenerator.generate_random_movie_published(),
            "genreId": DataGenerator.generate_random_movie_genre_id(),
        }
        response = api_manager_admin.movies_api.create_movie(
            duplicate_data, expected_status=409
        )
        assert response.status_code == 409

    def test_create_movie_invalid_body_400(self, api_manager_admin):
        """Негатив: создание без обязательных полей — 400."""
        invalid_data = {"name": "Только название"}

        response = api_manager_admin.movies_api.create_movie(
            invalid_data, expected_status=400
        )
        assert response.status_code == 400

    # --- PATCH /movies/{id} ---

    def test_edit_movie_success(self, api_manager_admin, created_movie):
        """Позитив: редактирование фильма — 200, данные обновлены."""
        movie_id = created_movie["id"]
        update_data = {
            "name": created_movie["name"] + " (обновлён)",
            "description": "Новое описание",
            "price": 300,
            "location": "SPB",
            "imageUrl": created_movie.get("imageUrl", "https://image.url"),
            "published": True,
            "genreId": created_movie["genreId"],
        }
        response = api_manager_admin.movies_api.edit_movie(movie_id, update_data)
        data = response.json()

        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["price"] == update_data["price"]
        assert data["location"] == update_data["location"]

    def test_edit_movie_not_found_404(self, api_manager_admin, movie_data):
        """Негатив: редактирование несуществующего фильма — 404."""
        response = api_manager_admin.movies_api.edit_movie(
            99999999, movie_data, expected_status=404
        )
        assert response.status_code == 404

    # --- DELETE /movies/{id} ---

    def test_delete_movie_not_found_404(self, api_manager_admin):
        """Негатив: удаление несуществующего фильма — 404."""
        response = api_manager_admin.movies_api.delete_movie(
            99999999, expected_status=404
        )
        assert response.status_code == 404
