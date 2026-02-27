"""
Обёртка над requests: единый метод send_request, логирование запросов/ответов, проверка статуса.
"""
import json
import logging
import os
from typing import Dict, Optional

import requests
from pydantic import BaseModel

from constants.constants import GREEN, RESET, RED


class CustomRequester:
    """
    Базовый класс для API-клиентов: общая отправка запросов, заголовки, логи в виде curl.
    При несовпадении статуса ответа с expected_status выбрасывает ValueError.
    """
    base_headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, session: requests.Session, base_url: str) -> None:
        """
        :param session: Объект requests.Session для запросов.
        :param base_url: Базовый URL API (без завершающего слэша или с ним).
        """
        self.session = session
        self.base_url = base_url
        self.headers = self.base_headers.copy()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def send_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict | BaseModel] = None,
        params: Optional[Dict[str, str]] = None,
        expected_status: int = 200,
        need_logging: bool = True,
    ) -> requests.Response:
        """
        Отправляет HTTP-запрос и проверяет статус ответа.
        :param method: HTTP-метод (GET, POST, PATCH, DELETE и т.д.).
        :param endpoint: Путь эндпоинта (например, "/login"), склеивается с base_url.
        :param data: Тело запроса: dict или Pydantic BaseModel (сериализуется в JSON).
        :param params: Query-параметры (словарь).
        :param expected_status: Ожидаемый HTTP-статус; при несовпадении — ValueError.
        :param need_logging: Логировать ли запрос и ответ в виде curl.
        :return: requests.Response.
        """

        if isinstance(data, BaseModel):
            data = json.loads(data.model_dump_json(exclude_unset=True))
        # Support Pydantic models for query params as well
        if isinstance(params, BaseModel):
            # convert to dict excluding None values
            params = params.model_dump(exclude_none=True)

        response = self.session.request(
            method, f"{self.base_url}{endpoint}", json=data, params=params, headers=self.headers
        )

        if need_logging:
            self.log_request_and_response(response)

        if response.status_code != expected_status:
            body = response.text
            raise ValueError(
                f"Unexpected status code: {response.status_code}. Expected: {expected_status}\nResponse body: {body}"
            )

        return response

    def _update_session_headers(self, headers: Dict[str, str]) -> None:
        """
        Добавляет заголовки в self.headers и в session.headers (например, Authorization: Bearer ...).
        :param headers: Словарь имя_заголовка -> значение.
        """
        self.headers.update(headers)
        self.session.headers.update(headers)

    def log_request_and_response(self, response: requests.Response) -> None:
        """
        Логгирование запросов и ответов. Настройки логгирования описаны в pytest.ini
        Преобразует вывод в curl-like (-H хэдэеры), (-d тело)

        :param response: Объект response получаемый из метода "send_request"
        """

        try:
            request = response.request
            headers = " \\\n".join([f"=H '{header}: {value}'" for header, value in request.headers.items()])
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                elif isinstance(request.body, str):
                    body = request.body
                body = f"-d '{body}' \n" if body != '{}' else ''

            # Логируем запрос
            self.logger.info(f"\n{'=' * 40} REQUEST {'=' * 40}")
            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl - X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            # Обрабатываем ответ
            response_status = response.status_code
            is_success = response.ok
            response_data = response.text

            # Попытка сформировать JSON
            try:
                response_data = json.dumps(json.loads(response.text), indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                pass

            # Логируем ответ
            self.logger.info(f"\n{'=' * 40} RESPONSE {'=' * 40}")
            if not is_success:
                self.logger.info(
                    f"\tSTATUS_CODE: {RED}{response_status}{RESET}\n"
                    f"\tDATA: {RED}{response_data}{RESET}"
                )
            else:
                self.logger.info(
                    f"\tSTATUS_CODE: {GREEN}{response_status}{RESET}\n"
                    f"\tDATA: \n{response_data}"
                )
            self.logger.info(f"{'=' * 80}\n")

        except Exception as e:
            self.logger.error(f"\nLogging failed: {type(e)} - {e}")