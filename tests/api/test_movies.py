"""
Тесты для эндпоинта /movies (API Movies).
Операции создания/редактирования/удаления — от имени SUPER_ADMIN (фикстура super_admin).
"""
import pytest

from services.movie_service import MovieService
from entities.user import User
from models.base_models import MoviePayload, MovieResponse, MoviesListResponse
from utils.data_generator import DataGenerator

pytestmark = pytest.mark.api

class TestMoviesApi:
    """Позитивные и негативные проверки API Movies."""

    # --- GET /movies ---

    @pytest.mark.slow
    def test_get_movies_success(self, super_admin: User) -> None:
        """Позитив: получение списка фильмов возвращает 200 и корректную структуру."""
        response = super_admin.api.movies_api.get_movies()
        data = MoviesListResponse(**response.json())
        assert data.pageSize >= 1
        assert isinstance(data.movies, list)


    def test_get_movies_with_filters_page_size(self, super_admin: User) -> None:
        """Позитив: фильтр pageSize ограничивает количество записей на странице."""
        page_size = 3
        response = super_admin.api.movies_api.get_movies(params={"pageSize": str(page_size)})
        data = MoviesListResponse(**response.json())

        assert data.pageSize == page_size
        assert len(data.movies) <= page_size

    @pytest.mark.smoke
    @pytest.mark.parametrize("min_price,max_price,genre_id,location", [("100", "500", "1", "MSK"), ("200", "300", "4", "MSK")])
    def test_get_movies_with_filters_min_max_price(self, super_admin: User, min_price: str ,max_price: str, genre_id: str, location: str) -> None:
        """Позитив: фильтры minPrice и maxPrice сужают выборку по цене."""
        response = super_admin.api.movies_api.get_movies(
            params={"minPrice": min_price, "maxPrice": max_price, "genreId": genre_id, "locations": location}
        )
        data = MoviesListResponse(**response.json())

        for movie in data.movies:
            assert int(min_price) <= movie.price <= int(max_price)
            assert movie.genreId == int(genre_id)
            assert movie.location == location

    def test_get_movies_with_filter_locations(self, super_admin: User) -> None:
        """Позитив: фильтр locations (массив MSK/SPB) возвращает только подходящие фильмы."""
        response = super_admin.api.movies_api.get_movies(params={"locations": "MSK"})
        data = MoviesListResponse(**response.json())

        for movie in data.movies:
            assert movie.location == "MSK"

    def test_get_movies_invalid_params_400(self, super_admin: User) -> None:
        """Негатив: неверные параметры (pageSize вне 1–20) — 400."""
        response = super_admin.api.movies_api.get_movies(
            params={"pageSize": "0"},
            expected_status=400,
        )
        assert response.status_code == 400

    # --- GET /movies/{id} ---

    def test_get_movie_by_id_success(self, created_movie: MovieResponse, super_admin: User) -> None:
        """Позитив: получение фильма по id возвращает 200 и данные фильма."""
        response = super_admin.api.movies_api.get_movie(created_movie.id)
        data = MovieResponse(**response.json())

        assert data.id == created_movie.id
        assert data.name == created_movie.name
        assert data.price == created_movie.price
        assert data.description == created_movie.description
        assert data.location == created_movie.location
        assert data.reviews is not None

    def test_get_movie_not_found_404(self, super_admin: User) -> None:
        """Негатив: запрос по несуществующему id — 404."""
        response = super_admin.api.movies_api.get_movie(99999999, expected_status=404)
        assert response.status_code == 404
        assert "Фильм не найден" in response.json().get("message", "")

    # --- POST /movies ---

    @pytest.mark.slow
    def test_create_movie_success(self, super_admin: User, movie_data: MoviePayload) -> None:
        """Позитив: создание фильма с данными из фикстуры — 201 (SUPER_ADMIN)."""
        response = super_admin.api.movies_api.create_movie(movie_data.model_dump())
        data = MovieResponse(**response.json())

        assert data.name == movie_data.name
        assert data.price == movie_data.price
        assert data.description == movie_data.description
        assert data.location == movie_data.location

        super_admin.api.movies_api.delete_movie(data.id)

    def test_create_movie_user_forbidden_403(self, common_user: User, movie_data: MoviePayload) -> None:
        """Негатив: пользователь с ролью USER не может создать фильм — 403."""
        response = common_user.api.movies_api.create_movie(movie_data.model_dump(), expected_status=403)
        assert response.status_code == 403

    def test_create_movie_duplicate_name_409(self, super_admin: User, created_movie: MovieResponse) -> None:
        """Негатив: создание фильма с уже существующим названием — 409."""
        duplicate_data = {
            "name": created_movie.name,
            "price": DataGenerator.generate_random_movie_price(),
            "description": DataGenerator.generate_random_movie_description(),
            "location": DataGenerator.generate_random_movie_location(),
            "imageUrl": DataGenerator.generate_random_movie_image_url(),
            "published": DataGenerator.generate_random_movie_published(),
            "genreId": DataGenerator.generate_random_movie_genre_id(),
        }
        response = super_admin.api.movies_api.create_movie(
            duplicate_data, expected_status=409
        )
        assert response.status_code == 409

    def test_create_movie_invalid_body_400(self, super_admin: User) -> None:
        """Негатив: создание без обязательных полей — 400."""
        invalid_data = {"name": "Только название"}

        response = super_admin.api.movies_api.create_movie(
            invalid_data, expected_status=400
        )
        assert response.status_code == 400

    # --- PATCH /movies/{id} ---

    def test_edit_movie_success(self, super_admin: User, created_movie: MovieResponse) -> None:
        """Позитив: редактирование фильма — 200, данные обновлены (SUPER_ADMIN)."""
        update_data = {
            "name": created_movie.name + " (обновлён)",
            "description": "Новое описание",
            "price": 300,
            "location": "SPB",
            "imageUrl": created_movie.imageUrl or "https://image.url",
            "published": True,
            "genreId": created_movie.genreId,
        }
        response = super_admin.api.movies_api.edit_movie(created_movie.id, update_data)
        data = MovieResponse(**response.json())

        assert data.name == update_data["name"]
        assert data.description == update_data["description"]
        assert data.price == update_data["price"]
        assert data.location == update_data["location"]

    def test_edit_movie_not_found_404(self, super_admin: User, movie_data: MoviePayload) -> None:
        """Негатив: редактирование несуществующего фильма — 404."""
        response = super_admin.api.movies_api.edit_movie(
            99999999, movie_data.model_dump(), expected_status=404
        )
        assert response.status_code == 404

    # --- DELETE /movies/{id} ---

    def test_delete_movie_success_super_admin(
        self, super_admin: User, movie_data: MoviePayload
    ) -> None:
        """Позитив: только SUPER_ADMIN может удалить фильм — 200."""
        response = super_admin.api.movies_api.create_movie(movie_data.model_dump())
        movie = MovieResponse(**response.json())
        delete_response = super_admin.api.movies_api.delete_movie(movie.id, expected_status=200)
        assert delete_response.status_code == 200

    @pytest.mark.parametrize("user_fixture,expected_status", [
        ("common_user", 403),
        ("admin_user", 403),
    ])
    def test_delete_movie_forbidden_by_role(
        self,
        request: pytest.FixtureRequest,
        user_fixture: str,
        expected_status: int,
        created_movie: MovieResponse,
    ) -> None:
        """Негатив: USER и ADMIN не могут удалять фильмы — 403 (по доке только SUPER_ADMIN)."""
        user: User = request.getfixturevalue(user_fixture)
        response = user.api.movies_api.delete_movie(
            created_movie.id, expected_status=expected_status
        )
        assert response.status_code == expected_status

    def test_delete_movie_not_found_404(self, super_admin: User) -> None:
        """Негатив: удаление несуществующего фильма — 404."""
        response = super_admin.api.movies_api.delete_movie(
            99999999, expected_status=404
        )
        assert response.status_code == 404

    def test_create_movie_and_delete_in_db(
        self, movie_service: MovieService, movie_data: MoviePayload
    ) -> None:
        assert movie_service.get_movie_by_name(movie_data.name) is None
        movie = movie_service.create_movie(movie_data)
        assert movie_service.get_movie_by_name(movie_data.name) is not None
        movie_service.delete_movie(movie)
        assert movie_service.get_movie_by_name(movie_data.name) is None
