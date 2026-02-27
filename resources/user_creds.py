"""Загрузка учётных данных супер-админа из .env."""

import os
from dotenv import load_dotenv

load_dotenv()


class SuperAdminCreds:
    """Контейнер с именем пользователя и паролем супер-админа, берутся из окружения."""

    USERNAME: str = os.getenv("SUPER_ADMIN_USERNAME")
    PASSWORD: str = os.getenv("SUPER_ADMIN_PASSWORD")