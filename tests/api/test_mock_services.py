import datetime
import os
import sys

import allure
import pytest
from pytest_check import check
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

pytestmark = [pytest.mark.api, pytest.mark.regression]


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


@allure.label("qa_name", "Viktor")
class TestTodayIsHolidayServiceAPI:
    @staticmethod
    def stub_get_worldclockap_time():
        class StubWorldClockResponse:
            currentDateTime = "2025-05-09T00:00Z"  # День Победы

        return StubWorldClockResponse()

    @allure.title("Проверка worldclockapi через WireMock")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.mock_smoke
    @pytest.mark.smoke
    def test_worldclockap(self):
        """Проверка работоспособности worldclockapi через WireMock stub."""
        with allure.step("Настройка WireMock и запрос к worldclockapi"):
            _setup_worldclockap_wiremock()
            world_clock_response = get_worldclockap_time(base_url="http://localhost:8088")
            current_date_time = world_clock_response.currentDateTime
        with allure.step("Проверка совпадения даты"):
            assert current_date_time == datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ"), "Дата не совпадает"

    @allure.title("Проверка what_is_today через WireMock")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.mock_smoke
    @pytest.mark.smoke
    def test_what_is_today(self):
        """Проверка Fake-сервиса what_is_today с данными из WireMock."""
        with allure.step("Получение времени из worldclockapi и запрос what_is_today"):
            _setup_worldclockap_wiremock()
            world_clock_response = get_worldclockap_time(base_url="http://localhost:8088")
            what_is_today_response = requests.post(
                "http://127.0.0.1:16002/what_is_today",
                json=DateTimeRequest(currentDateTime=world_clock_response.currentDateTime).model_dump(),
            )
        with allure.step("Проверка ответа what_is_today"):
            with check:
                check.equal(what_is_today_response.status_code, 200, "Удаленный сервис недоступен")
                what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
                check.equal(what_is_today_data.message, "Сегодня нет праздников в России.", "Сегодня нет праздника!")

    @allure.title("Проверка Fake-сервиса worldclockapi (порт 16001)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_fake_worldclockap(self):
        """Проверка Fake-сервиса worldclockapi (FastAPI на порту 16001)."""
        with allure.step("Запрос к Fake worldclockapi"):
            world_clock_response = get_worldclockap_time(base_url=FAKE_WORLDCLOCK_URL)
            current_date_time = world_clock_response.currentDateTime
        with allure.step("Проверка совпадения даты"):
            assert current_date_time == datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ"), "Дата не совпадает"

    @allure.title("Проверка what_is_today с Fake worldclockapi")
    @allure.severity(allure.severity_level.NORMAL)
    def test_fake_what_is_today(self):
        """Проверка what_is_today с использованием Fake-сервиса worldclockapi."""
        with allure.step("Запрос к Fake worldclockapi и what_is_today"):
            world_clock_response = get_worldclockap_time(base_url=FAKE_WORLDCLOCK_URL)
            what_is_today_response = requests.post(
                "http://127.0.0.1:16002/what_is_today",
                json=DateTimeRequest(currentDateTime=world_clock_response.currentDateTime).model_dump(),
            )
        with allure.step("Проверка ответа"):
            with check:
                check.equal(what_is_today_response.status_code, 200, "Удаленный сервис недоступен")
                what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
                check.equal(what_is_today_data.message, "Сегодня нет праздников в России.", "Сегодня нет праздника!")

    @allure.title("what_is_today с Mock — Новый год")
    @allure.severity(allure.severity_level.MINOR)
    def test_what_is_today_BY_MOCK(self, mocker):
        """Подмена get_worldclockap_time через Mock (2025-01-01) — ожидаем «Новый год»."""
        with allure.step("Мокаем get_worldclockap_time (2025-01-01)"):
            mocker.patch(
                "test_mock_services.get_worldclockap_time",
                return_value=Mock(currentDateTime="2025-01-01T00:00Z"),
            )
        with allure.step("Запрос what_is_today с замоканной датой"):
            world_clock_response = get_worldclockap_time()
            what_is_today_response = requests.post(
                "http://127.0.0.1:16002/what_is_today",
                json=DateTimeRequest(currentDateTime=world_clock_response.currentDateTime).model_dump(),
            )
        with allure.step("Проверка: ожидаем «Новый год»"):
            with check:
                check.equal(what_is_today_response.status_code, 200, "Удаленный сервис недоступен")
                what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
                check.equal(what_is_today_data.message, "Новый год", "ДОЛЖЕН БЫТЬ НОВЫЙ ГОД!")

    @allure.title("what_is_today с Stub — День Победы")
    @allure.severity(allure.severity_level.MINOR)
    def test_what_is_today_BY_STUB(self, monkeypatch):
        """Подмена get_worldclockap_time через Stub (День Победы) — ожидаем «День Победы»."""
        with allure.step("Подменяем get_worldclockap_time на Stub (День Победы)"):
            monkeypatch.setattr(sys.modules[__name__], "get_worldclockap_time", self.stub_get_worldclockap_time)
        with allure.step("Запрос what_is_today с Stub-датой"):
            world_clock_response = get_worldclockap_time()
            what_is_today_response = requests.post(
                "http://127.0.0.1:16002/what_is_today",
                json=DateTimeRequest(currentDateTime=world_clock_response.currentDateTime).model_dump(),
            )
        with allure.step("Проверка: ожидаем «День Победы»"):
            with check:
                check.equal(what_is_today_response.status_code, 200, "Удаленный сервис недоступен")
                what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
                check.equal(what_is_today_data.message, "День Победы", "ДОЛЖЕН БЫТЬ ДЕНЬ ПОБЕДЫ!")

