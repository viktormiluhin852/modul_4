import allure
import requests


# Настройка WireMock для мока
def setup_wiremock_mock():
    url = "http://localhost:8088/__admin/mappings"
    payload = {
        "request": {
            "method": "GET",
            "url": "/gismeteo/get/weather" #мы указываем что если ктото сделате запрос на ручку
											                     #http://localhost:8080/gismeteo/get/weather
        },
        "response": {
            "status": 200,# ему вернется ответ с кодом 200
            "body": '{"temperature": 25}',
            "headers": {
                "Content-Type": "application/json"
            }
        }
    }
    response = requests.post(url, json=payload) #Отправляем запрос на наш WireMock

@allure.title("Тест WireMock — мок /gismeteo/get/weather")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("qa_name", "Viktor")
def test_wiremock():
    """Проверка WireMock: настройка мока и запрос возвращает ожидаемый ответ."""
    with allure.step("Настройка WireMock для /gismeteo/get/weather"):
        setup_wiremock_mock()
    with allure.step("GET /gismeteo/get/weather — проверка ответа"):
        response = requests.get("http://localhost:8088/gismeteo/get/weather")
    with allure.step("Проверка: статус 200 и тело ответа"):
        assert response.status_code == 200
        assert response.json() == {"temperature": 25}