import random
import time

import allure
import pytest
from pytest_check import check
from requests import Session

from db_models.transaction import AccountTransactionTemplate
from utils.data_generator import DataGenerator
pytestmark = [pytest.mark.api, pytest.mark.regression]
@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
@allure.label("qa_name", "Viktor")
class TestAccountTransactionTemplate:

    @allure.story("Корректность перевода денег между двумя счетами")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Тест перевода денег между счетами 200 рублей")
    @pytest.mark.transactions_smoke
    @pytest.mark.smoke
    def test_accounts_transaction_template(self, db_session: Session):
        """
        Этот тест проверяет корректность перевода денег между двумя счетами.
        Шаги:
        1. Создание двух счетов: Stan и Bob.
        2. Перевод 200 единиц от Stan к Bob.
        3. Проверка изменения балансов.
        4. Очистка тестовых данных.
        """
        # ====================================================================== Подготовка к тесту
        with allure.step("Создание тестовых данных в базе данных: счета Stan и Bob"):
            stan = AccountTransactionTemplate(user=f"Stan_{DataGenerator.generate_random_int(10)}", balance=1000)
            bob = AccountTransactionTemplate(user=f"Bob_{DataGenerator.generate_random_int(10)}", balance=500)
            db_session.add_all([stan, bob])
            db_session.commit()

        @allure.step("Функция перевода денег: transfer_money")
        @allure.description("""
            функция выполняющая транзакцию, имитация вызова функции на стороне тестируемого сервиса
            и вызывая метод transfer_money, мы какбудтобы делем запрос в api_manager.movies_api.transfer_money
            """)
        def transfer_money(session, from_account, to_account, amount):
            with allure.step(" Получаем счета"):
                from_account = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
                to_account = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()

            with allure.step("Проверяем, что на счете достаточно средств"):
                if from_account.balance < amount:
                    raise ValueError("Недостаточно средств на счете")

            with allure.step("Выполняем перевод"):
                from_account.balance -= amount
                to_account.balance += amount

            with allure.step("Сохраняем изменения"):
                session.commit()

        # ====================================================================== Тест
        with allure.step("Проверяем начальные балансы"):
            with check:
                check.equal(stan.balance, 1000)
                check.equal(bob.balance, 500)

        try:
            with allure.step("Выполняем перевод 200 единиц от stan к bob"):
                transfer_money(db_session, from_account=stan.user, to_account=bob.user, amount=200)

            with allure.step("Проверяем, что балансы изменились"):
                with check:
                    check.equal(stan.balance, 800)
                    check.equal(bob.balance, 700)

        except Exception as e:
            with allure.step("ОШИБКА откаты транзакции"):
                db_session.rollback()

            pytest.fail(f"Ошибка при переводе денег: {e}")

        finally:
            with allure.step("Удаляем данные для тестирования из базы"):
                db_session.delete(stan)
                db_session.delete(bob)
                db_session.commit()


@pytest.fixture  # была добавлена в файл conftest.py
def delay_between_retries():
    time.sleep(2)  # Задержка в 2 секунды\ это не обязательно но
    yield  # нужно понимать что такая возможность имеется


@allure.title("Тест с перезапусками")
@allure.severity(allure.severity_level.MINOR)
@allure.label("qa_name", "Viktor")
@pytest.mark.flaky(reruns=3)
def test_with_retries(delay_between_retries):
    """Демонстрация pytest-flaky: тест с reruns=3 при случайном падении."""
    with allure.step("Шаг 1: Проверка случайного значения"):
        result = random.choice([True, False])
        assert result, "Тест упал, потому что результат False"