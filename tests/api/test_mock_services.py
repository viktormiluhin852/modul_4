import datetime
import os
import sys

import pytz
import requests
from constants.constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from api.api_manager import ApiManager
from enums.roles import Roles
from models.base_models import RegisterUserResponse, UserPayload
from pytest_mock import mocker
from unittest.mock import Mock

import requests
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


# Модель Pydantic для ответа сервера worldclockapi
class WorldClockResponse(BaseModel):
    id: str = Field(alias="$id")  # Используем алиас для поля "$id"
    currentDateTime: str
    utcOffset: str
    isDayLightSavingsTime: bool
    dayOfTheWeek: str
    timeZoneName: str
    currentFileTime: int
    ordinalDate: str
    serviceResponse: None

    model_config = ConfigDict(populate_by_name=True)


# Модель для запроса к сервису TodayIsHoliday
class DateTimeRequest(BaseModel):
    currentDateTime: str  # Формат: "2025-02-13T21:43Z"


# Модель для ответа от сервиса TodayIsHoliday
class WhatIsTodayResponse(BaseModel):
    message: str


WORLDCLOCK_BASE_URL = os.getenv("WORLDCLOCK_API_URL", "http://worldclockapi.com")
FAKE_WORLDCLOCK_URL = "http://127.0.0.1:16001/fake/worldclockapi"


def _setup_worldclockap_wiremock(url: str = "http://localhost:8088") -> None:
    """Настраивает WireMock: GET /api/json/utc/now → fake worldclockapi."""
    now_str = datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ")
    requests.post(
        f"{url}/__admin/mappings",
        json={
            "request": {"method": "GET", "urlPathPattern": "/api/json/utc/now"},
            "response": {
                "status": 200,
                "jsonBody": {
                    "$id": "1",
                    "currentDateTime": now_str,
                    "utcOffset": "00:00:00",
                    "isDayLightSavingsTime": False,
                    "dayOfTheWeek": "Sunday",
                    "timeZoneName": "UTC",
                    "currentFileTime": 133031520000000000,
                    "ordinalDate": "2025-54",
                    "serviceResponse": None,
                },
            },
        },
    )


def get_worldclockap_time(base_url: str = None) -> WorldClockResponse:
    # Выполняем GET-запрос
    base = base_url or WORLDCLOCK_BASE_URL
    response = requests.get(f"{base}/api/json/utc/now")
    # Проверяем статус ответа
    assert response.status_code == 200, "Удаленный сервис недоступен"
    # Парсим JSON-ответ с использованием Pydantic модели
    return WorldClockResponse(**response.json())


class TestTodayIsHolidayServiceAPI:
    @staticmethod
    def stub_get_worldclockap_time():
        class StubWorldClockResponse:
            currentDateTime = "2025-05-09T00:00Z"  # День Победы

        return StubWorldClockResponse()

    # worldclockap
    def test_worldclockap(self):  # проверка работоспособности сервиса worldclockap
        _setup_worldclockap_wiremock()
        world_clock_response = get_worldclockap_time(base_url="http://localhost:8088")
        # Выводим текущую дату и время
        current_date_time = world_clock_response.currentDateTime
        print(f"Текущая дата и время: {current_date_time=}")

        assert current_date_time == datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ"), "Дата не совпадает"

    def test_what_is_today(self):  # проверка работоспособности Fake сервиса what_is_today
        _setup_worldclockap_wiremock()
        world_clock_response = get_worldclockap_time(base_url="http://localhost:8088")

        what_is_today_response = requests.post("http://127.0.0.1:16002/what_is_today",
                                               json=DateTimeRequest(
                                                   currentDateTime=world_clock_response.currentDateTime).model_dump())

        # Проверяем статус ответа от тестируемогосервиса
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ от тестируемого сервиса с использованием Pydantic модели
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        # Проводим валидацию ответа тестируемого сервиса
        assert what_is_today_data.message == "Сегодня нет праздников в России.", "Сегодня нет праздника!"

    def test_fake_worldclockap(self):
        """Проверка Fake-сервиса worldclockapi (FastAPI на порту 16001)."""
        world_clock_response = get_worldclockap_time(base_url=FAKE_WORLDCLOCK_URL)
        current_date_time = world_clock_response.currentDateTime
        print(f"Текущая дата и время: {current_date_time=}")
        assert current_date_time == datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ"), "Дата не совпадает"

    def test_fake_what_is_today(self):
        """Проверка what_is_today с использованием Fake-сервиса worldclockapi."""
        world_clock_response = get_worldclockap_time(base_url=FAKE_WORLDCLOCK_URL)
        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            json=DateTimeRequest(currentDateTime=world_clock_response.currentDateTime).model_dump(),
        )
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "Сегодня нет праздников в России.", "Сегодня нет праздника!"

    def test_what_is_today_BY_MOCK(self, mocker):
        # Создаем мок для функции get_worldclockap_time
        mocker.patch(
            "test_mock_services.get_worldclockap_time",
            # Указываем путь к функции в нашем модуле (формат файл.класс.метод)
            # либо имя_файла.имя_метода если он находится  вэтом же файле
            return_value=Mock(
                currentDateTime="2025-01-01T00:00Z"  # Фиксированная дата для возврата из мок функции "1 января"
            )
        )

        # Выполним тело предыдущего теста еще раз
        world_clock_response = get_worldclockap_time()  # = "2025-01-01T00:00Z"

        what_is_today_response = requests.post("http://127.0.0.1:16002/what_is_today",
                                                json=DateTimeRequest(
                                                    currentDateTime=world_clock_response.currentDateTime).model_dump())

        # Проверяем статус ответа от тестируемого сервиса
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ от тестируемого сервиса с использованием Pydantic модели
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())

        assert what_is_today_data.message == "Новый год", "ДОЛЖЕН БЫТЬ НОВЫЙ ГОД!"

    # Тест с использованием Stub
    def test_what_is_today_BY_STUB(self, monkeypatch):
        # Подменяем реальную функцию get_worldclockap_time на Stub
        monkeypatch.setattr(sys.modules[__name__], "get_worldclockap_time", self.stub_get_worldclockap_time)
        # или же можем просто напрямую взять значение из Stub world_clock_response = stub_get_worldclockap_time()

        # Выполним тело предыдущего теста еще раз
        world_clock_response = get_worldclockap_time() # Произойдет вызов Stub, возвращающего "2025-01-01T00:00Z"

        # Выполняем запрос к тестируемому сервису
        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            json=DateTimeRequest(currentDateTime=world_clock_response.currentDateTime).model_dump()
        )

        # Проверяем статус ответа от тестируемого сервиса
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ от тестируемого сервиса с использованием Pydantic модели
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        # Проверяем, что ответ соответствует ожидаемому
        assert what_is_today_data.message == "День Победы", "ДОЛЖЕН БЫТЬ ДЕНЬ ПОБЕДЫ!"

