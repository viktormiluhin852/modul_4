from pydantic import BaseModel, Field, field_validator
from typing import Optional
import datetime
from typing import List
from enums.roles import Roles

class UserPayload(BaseModel):
    id: Optional[str] = None
    email: str
    fullName: str
    password: str
    passwordRepeat: str = Field(..., min_length=1, max_length=20, description="passwordRepeat должен полностью совпадать с полем password")
    roles: list[Roles] = [Roles.USER]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator("passwordRepeat")
    def check_password_repeat(cls, value: str, info) -> str:
        # Проверяем совпадение паролей
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value



class RegisterUserResponse(BaseModel):
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str = Field(min_length=1, max_length=100, description="Полное имя пользователя")
    verified: bool
    banned: Optional[bool] = False
    roles: List[Roles]
    createdAt: str = Field(description="Дата и время создания пользователя в формате ISO 8601")

    @field_validator("createdAt")
    def validate_created_at(cls, value: str) -> str:
        # Валидатор для проверки формата даты и времени (ISO 8601).
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value


class LoginUserInfo(BaseModel):
    """Данные пользователя в ответе POST /login."""
    id: str
    email: str
    fullName: str
    roles: List[Roles]

class LoginResponse(BaseModel):
    """Ответ POST /login: accessToken и данные пользователя."""
    accessToken: str
    user: LoginUserInfo
    refreshToken: Optional[str] = None
    expiresIn: Optional[int] = None


class MoviePayload(BaseModel):
    """Тело запроса POST /movies и PATCH /movies/{id}."""
    name: str
    price: int
    description: str
    imageUrl: Optional[str] = None
    location: str
    published: bool = True
    genreId: int = 1


class MovieResponse(BaseModel):
    """Один фильм в ответе GET /movies/{id}, POST /movies, PATCH /movies/{id} и в элементе списка GET /movies."""
    id: int
    name: str
    price: int
    description: str
    location: str
    imageUrl: Optional[str] = None
    published: bool = True
    genreId: int = 1
    reviews: Optional[List[dict]] = None


class MoviesListResponse(BaseModel):
    """Ответ GET /movies: список фильмов с пагинацией."""
    movies: List[MovieResponse]
    count: int
    page: int
    pageSize: int
    pageCount: int
