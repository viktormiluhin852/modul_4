"""
Тесты для эндпоинта /movies (API Movies).
Операции создания/редактирования/удаления — от имени SUPER_ADMIN (фикстура super_admin).
"""
import allure
import pytest
from pytest_check import check

from services.movie_service import MovieService
from entities.user import User
from models.base_models import (
    GetMoviesParams,
    MoviePatchPayload,
    MoviePayload,
    MovieResponse,
    MoviesListResponse,
)
from utils.data_generator import DataGenerator

pytestmark = pytest.mark.api


@allure.label("qa_name", "Viktor")
class TestMoviesApi:
    """Позитивные и негативные проверки API Movies."""

    # --- GET /movies ---

    @allure.title("Получение списка фильмов — 200, корректная структура")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.slow
    def test_get_movies_success(self, super_admin: User) -> None:
        """Позитив: получение списка фильмов возвращает 200 и корректную структуру (pageSize, movies)."""
        with allure.step("GET /movies — получение списка фильмов"):
            response = super_admin.api.movies_api.get_movies()
            data = MoviesListResponse(**response.json())

        with allure.step("Проверка структуры ответа: pageSize >= 1, movies — список"):
            with check:
                check.is_true(data.pageSize >= 1)
                check.equal(isinstance(data.movies, list), True)


    @allure.title("Фильтр pageSize ограничивает количество записей")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_movies_with_filters_page_size(self, super_admin: User) -> None:
        """Позитив: фильтр pageSize ограничивает количество записей на странице."""
        page_size = 3
        with allure.step(f"GET /movies?pageSize={page_size}"):
            response = super_admin.api.movies_api.get_movies(
                params=GetMoviesParams(pageSize=str(page_size))
            )
            data = MoviesListResponse(**response.json())

        with allure.step("Проверка: pageSize и количество фильмов"):
            with check:
                check.equal(data.pageSize, page_size)
                check.is_true(len(data.movies) <= page_size)

    @allure.title("Фильтры minPrice, maxPrice, genreId, locations")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.parametrize("min_price,max_price,genre_id,location", [("100", "500", "1", "MSK"), ("200", "300", "4", "MSK")])
    def test_get_movies_with_filters_min_max_price(self, super_admin: User, min_price: str ,max_price: str, genre_id: str, location: str) -> None:
        """Позитив: фильтры minPrice, maxPrice, genreId, locations сужают выборку."""
        with allure.step(f"GET /movies с фильтрами minPrice={min_price}, maxPrice={max_price}, genreId={genre_id}, locations={location}"):
            response = super_admin.api.movies_api.get_movies(
                params=GetMoviesParams(
                    minPrice=min_price,
                    maxPrice=max_price,
                    genreId=genre_id,
                    locations=location,
                )
            )
            data = MoviesListResponse(**response.json())

        with allure.step("Проверка: все фильмы в диапазоне цен, genreId и location"):
            for movie in data.movies:
                assert int(min_price) <= movie.price <= int(max_price)
                assert movie.genreId == int(genre_id)
                assert movie.location == location

    @allure.title("Фильтр locations (MSK/SPB)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_movies_with_filter_locations(self, super_admin: User) -> None:
        """Позитив: фильтр locations возвращает только подходящие фильмы (MSK/SPB)."""
        with allure.step("GET /movies?locations=MSK"):
            response = super_admin.api.movies_api.get_movies(
                params=GetMoviesParams(locations="MSK")
            )
            data = MoviesListResponse(**response.json())

        with allure.step("Проверка: все фильмы с location=MSK"):
            for movie in data.movies:
                assert movie.location == "MSK"

    @allure.title("Негатив: неверные параметры pageSize — 400")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_movies_invalid_params_400(self, super_admin: User) -> None:
        """Негатив: неверные параметры (pageSize вне 1–20) — 400."""
        with allure.step("GET /movies?pageSize=0 — ожидаем 400"):
            response = super_admin.api.movies_api.get_movies(
                params=GetMoviesParams(pageSize="0"),
                expected_status=400,
            )

        with allure.step("Проверка: статус 400"):
            assert response.status_code == 400

    # --- GET /movies/{id} ---

    @allure.title("Получение фильма по id — 200, данные фильма")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_movie_by_id_success(self, created_movie: MovieResponse, super_admin: User) -> None:
        """Позитив: получение фильма по id возвращает 200 и данные фильма с reviews."""
        with allure.step(f"GET /movies/{created_movie.id} — получение фильма по id"):
            response = super_admin.api.movies_api.get_movie(created_movie.id)
            data = MovieResponse(**response.json())

        with allure.step("Проверка полей фильма и наличия reviews"):
            with check:
                check.equal(data.id, created_movie.id)
                check.equal(data.name, created_movie.name)
                check.equal(data.price, created_movie.price)
                check.equal(data.description, created_movie.description)
                check.equal(data.location, created_movie.location)
                check.is_true(data.reviews is not None)

    @allure.title("Негатив: запрос по несуществующему id — 404")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_movie_not_found_404(self, super_admin: User) -> None:
        """Негатив: запрос по несуществующему id — 404."""
        with allure.step("GET /movies/99999999 — ожидаем 404"):
            response = super_admin.api.movies_api.get_movie(99999999, expected_status=404)

        with allure.step("Проверка: статус 404 и сообщение «Фильм не найден»"):
            assert response.status_code == 404
            assert "Фильм не найден" in response.json().get("message", "")

    # --- POST /movies ---

    @allure.title("Создание фильма (SUPER_ADMIN) — 201")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.slow
    def test_create_movie_success(self, super_admin: User, movie_data: MoviePayload) -> None:
        """Позитив: создание фильма с данными из фикстуры — 201 (SUPER_ADMIN)."""
        with allure.step("POST /movies — создание фильма"):
            response = super_admin.api.movies_api.create_movie(movie_data)
            data = MovieResponse(**response.json())

        with allure.step("Проверка полей созданного фильма"):
            with check:
                check.equal(data.name, movie_data.name)
                check.equal(data.price, movie_data.price)
                check.equal(data.description, movie_data.description)
                check.equal(data.location, movie_data.location)

        with allure.step("DELETE /movies/{id} — удаление созданного фильма"):
            super_admin.api.movies_api.delete_movie(data.id)

    @allure.title("Негатив: USER не может создать фильм — 403")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_movie_user_forbidden_403(self, common_user: User, movie_data: MoviePayload) -> None:
        """Негатив: пользователь с ролью USER не может создать фильм — 403."""
        with allure.step("POST /movies от common_user — ожидаем 403 Forbidden"):
            response = common_user.api.movies_api.create_movie(movie_data, expected_status=403)

        with allure.step("Проверка: статус 403"):
            assert response.status_code == 403

    @allure.title("Негатив: дублирующееся название фильма — 409")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_movie_duplicate_name_409(self, super_admin: User, created_movie: MovieResponse) -> None:
        """Негатив: создание фильма с уже существующим названием — 409."""
        duplicate_data = MoviePayload(
            name=created_movie.name,
            price=DataGenerator.generate_random_movie_price(),
            description=DataGenerator.generate_random_movie_description(),
            location=DataGenerator.generate_random_movie_location(),
            imageUrl=DataGenerator.generate_random_movie_image_url(),
            published=DataGenerator.generate_random_movie_published(),
            genreId=DataGenerator.generate_random_movie_genre_id(),
        )
        with allure.step("POST /movies с дублирующимся name — ожидаем 409 Conflict"):
            response = super_admin.api.movies_api.create_movie(
                duplicate_data, expected_status=409
            )

        with allure.step("Проверка: статус 409"):
            assert response.status_code == 409

    @allure.title("Негатив: создание без обязательных полей — 400")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_movie_invalid_body_400(self, super_admin: User) -> None:
        """Негатив: создание без обязательных полей — 400."""
        invalid_data = MoviePatchPayload(name="Только название")
        with allure.step("POST /movies с неполным телом — ожидаем 400"):
            response = super_admin.api.movies_api.create_movie(
                invalid_data, expected_status=400
            )

        with allure.step("Проверка: статус 400"):
            assert response.status_code == 400

    # --- PATCH /movies/{id} ---

    @allure.title("Редактирование фильма (SUPER_ADMIN) — 200")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_edit_movie_success(self, super_admin: User, created_movie: MovieResponse) -> None:
        """Позитив: редактирование фильма — 200, данные обновлены (SUPER_ADMIN)."""
        update_data = MoviePatchPayload(
            name=created_movie.name + " (обновлён)",
            description="Новое описание",
            price=300,
            location="SPB",
            imageUrl=created_movie.imageUrl or "https://image.url",
            published=True,
            genreId=created_movie.genreId,
        )
        with allure.step(f"PATCH /movies/{created_movie.id} — редактирование фильма"):
            response = super_admin.api.movies_api.edit_movie(created_movie.id, update_data)
            data = MovieResponse(**response.json())

        with allure.step("Проверка обновлённых полей"):
            with check:
                check.equal(data.name, update_data.name)
                check.equal(data.description, update_data.description)
                check.equal(data.price, update_data.price)
                check.equal(data.location, update_data.location)

    @allure.title("Негатив: редактирование несуществующего фильма — 404")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_movie_not_found_404(self, super_admin: User, movie_data: MoviePayload) -> None:
        """Негатив: редактирование несуществующего фильма — 404."""
        with allure.step("PATCH /movies/99999999 — ожидаем 404"):
            response = super_admin.api.movies_api.edit_movie(
                99999999,
                MoviePatchPayload(
                    name=movie_data.name,
                    price=movie_data.price,
                    description=movie_data.description,
                    location=movie_data.location,
                    imageUrl=movie_data.imageUrl,
                    published=True,
                    genreId=movie_data.genreId,
                ),
                expected_status=404,
            )

        with allure.step("Проверка: статус 404"):
            assert response.status_code == 404

    # --- DELETE /movies/{id} ---

    @allure.title("Удаление фильма (SUPER_ADMIN) — 200")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_movie_success_super_admin(
        self, super_admin: User, movie_data: MoviePayload
    ) -> None:
        """Позитив: только SUPER_ADMIN может удалить фильм — 200."""
        with allure.step("POST /movies — создание фильма для удаления"):
            response = super_admin.api.movies_api.create_movie(movie_data)
            movie = MovieResponse(**response.json())

        with allure.step(f"DELETE /movies/{movie.id} — удаление фильма (SUPER_ADMIN)"):
            delete_response = super_admin.api.movies_api.delete_movie(movie.id, expected_status=200)

        with allure.step("Проверка: статус 200"):
            assert delete_response.status_code == 200

    @allure.title("Негатив: USER и ADMIN не могут удалять фильмы — 403")
    @allure.severity(allure.severity_level.NORMAL)
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
        """Негатив: USER и ADMIN не могут удалять фильмы — 403."""
        user: User = request.getfixturevalue(user_fixture)
        with allure.step(f"DELETE /movies/{created_movie.id} от {user_fixture} — ожидаем 403"):
            response = user.api.movies_api.delete_movie(
                created_movie.id, expected_status=expected_status
            )

        with allure.step(f"Проверка: статус {expected_status}"):
            assert response.status_code == expected_status

    @allure.title("Негатив: удаление несуществующего фильма — 404")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_movie_not_found_404(self, super_admin: User) -> None:
        """Негатив: удаление несуществующего фильма — 404."""
        with allure.step("DELETE /movies/99999999 — ожидаем 404"):
            response = super_admin.api.movies_api.delete_movie(
                99999999, expected_status=404
            )

        with allure.step("Проверка: статус 404"):
            assert response.status_code == 404

    @allure.title("Создание и удаление фильма через БД")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_movie_and_delete_in_db(
        self, movie_service: MovieService, movie_data: MoviePayload
    ) -> None:
        """Проверка movie_service: создание фильма, проверка в БД, удаление из БД."""
        with allure.step("Проверка: фильма с таким именем нет в БД"):
            assert movie_service.get_movie_by_name(movie_data.name) is None

        with allure.step("Создание фильма через movie_service"):
            movie = movie_service.create_movie(movie_data)

        with allure.step("Проверка: фильм появился в БД"):
            with check:
                check.is_true(movie_service.get_movie_by_name(movie_data.name) is not None)

        with allure.step("Удаление фильма из БД"):
            movie_service.delete_movie(movie)

        with allure.step("Проверка: фильм удалён из БД"):
            assert movie_service.get_movie_by_name(movie_data.name) is None
