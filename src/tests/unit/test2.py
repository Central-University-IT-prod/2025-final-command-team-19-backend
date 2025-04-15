import unittest
from unittest.mock import MagicMock
from datetime import date
from fastapi import HTTPException
from uuid import uuid4

from src.api.services.db_service import Client, Partner, Loyalty, ClientLoyaltyUsage
from src.api.repos.client_repository import ClientRepository



#
# class Client:
#     # Определяем атрибуты на уровне класса
#     client_id = None
#     name = None
#     email = None
#     password_hash = None
#     date_birthday = None
#     gender = None
#
#     def __init__(self, client_id, name, email, password_hash, date_birthday, gender):
#         self.client_id = client_id
#         self.name = name
#         self.email = email
#         self.password_hash = password_hash
#         self.date_birthday = date_birthday
#         self.gender = gender
#
# # Репозиторий клиента
# class ClientRepository:
#     def __init__(self, db):
#         self.db = db
#
#     def get_by_id(self, client_id):
#         return self.db.query(Client).filter(Client.client_id == str(client_id)).first()
#
#     def update_client(self, client_id, data):
#         existing_client = self.get_by_id(client_id)
#         if existing_client:
#             # Предполагаем, что data - объект с методом dict()
#             stmt = f"UPDATE clients SET {data.dict()} WHERE client_id = '{client_id}'"
#             self.db.execute(stmt)
#             self.db.commit()
#             self.db.refresh(existing_client)
#         else:
#             raise HTTPException(status_code=404,
#                                 detail={"message": "Такого клиента не существует"})
#         return existing_client

# Тестовые данные для обновления
class DummyData:
    def __init__(self, **kwargs):
        self._data = kwargs

    def dict(self):
        return self._data

class TestClientRepository(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.repo = ClientRepository(self.mock_session)
        self.client_id = str(uuid4())
        self.test_client = Client(
            client_id=self.client_id,
            name="Иван Иванов",
            email="ivan@example.com",
            password_hash="hashed_password",
            date_birthday=date(1990, 1, 1),
            gender="MALE"
        )

        # Настраиваем цепочку вызовов для метода query().filter().first()
        self.query_mock = MagicMock()
        self.filter_mock = MagicMock()
        self.query_mock.filter.return_value = self.filter_mock
        self.filter_mock.first.return_value = self.test_client
        self.mock_session.query.return_value = self.query_mock

    def test_get_by_id_success(self):
        """Успешное получение профиля пользователя по id."""
        result = self.repo.get_by_id(self.client_id)

        # Получаем фактический аргумент вызова filter
        called_args, _ = self.query_mock.filter.call_args
        actual_expression = called_args[0]

        # Импортируем необходимые модули
        from sqlalchemy.sql import operators
        from sqlalchemy.sql.elements import BindParameter

        # Проверяем левый операнд
        self.assertEqual(actual_expression.left, Client.client_id)

        # Проверяем оператор
        self.assertEqual(actual_expression.operator, operators.eq)

        # Проверяем правый операнд
        if isinstance(actual_expression.right, BindParameter):
            self.assertEqual(actual_expression.right.value, str(self.client_id))
        else:
            self.assertEqual(actual_expression.right, str(self.client_id))

        # Проверяем результат
        self.assertEqual(result, self.test_client)

    def test_update_client_success(self):
        """Успешное обновление профиля пользователя."""
        new_data = DummyData(name="Пётр Петров", email="petr@example.com")
        updated_client = self.repo.update_client(self.client_id, new_data)
        self.mock_session.execute.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once_with(self.test_client)
        self.assertEqual(updated_client, self.test_client)



    def test_update_nonexistent_client_raises_exception(self):
        """Попытка обновить несуществующего пользователя вызывает исключение."""
        self.filter_mock.first.return_value = None
        new_data = DummyData(name="Новый", email="new@example.com")
        with self.assertRaises(HTTPException) as context:
            self.repo.update_client(self.client_id, new_data)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, {"message": "Такого клиента не существует"})

    def test_get_loyalty_success(self):
        """Успешное получение списка программ лояльности для клиента."""
        # Пример данных, возвращаемых запросом
        loyalty_data = [
            # (Partner.name, Partner.picture_url, Loyalty.title, Loyalty.target_usages, ClientLoyaltyUsage.n_count)
            ("TBank", "https://dummyimage.com/83x374", "Кэшбэк по покупкам", 5, 3),
            ("TBank", "https://dummyimage.com/83x374", "Скидка на сервисы", 10, 1)
        ]

        # Настраиваем цепочку вызовов для метода get_loyalty
        query_mock = MagicMock()
        join_mock1 = MagicMock()
        join_mock2 = MagicMock()
        filter_mock = MagicMock()

        self.mock_session.query.return_value = query_mock
        query_mock.join.return_value = join_mock1
        join_mock1.join.return_value = join_mock2
        join_mock2.filter.return_value = filter_mock
        filter_mock.all.return_value = loyalty_data

        # Вызываем тестируемый метод
        result = self.repo.get_loyalty(self.client_id)

        # Ожидаемый результат
        expected_result = [
            {
                "name": "TBank",
                "picture_url": "https://dummyimage.com/83x374",
                "loyalties": [
                    {
                        "title": "Кэшбэк по покупкам",
                        "target_usages": 5,
                        "n_count": 3
                    },
                    {
                        "title": "Скидка на сервисы",
                        "target_usages": 10,
                        "n_count": 1
                    }
                ]
            }
        ]

        # Проверяем, что результат соответствует ожиданиям
        self.assertEqual(result, expected_result)

        # Проверяем, что цепочка методов была вызвана
        self.mock_session.query.assert_called_once_with(
            Partner.name,
            Partner.picture_url,
            Loyalty.title,
            Loyalty.target_usages,
            ClientLoyaltyUsage.n_count
        )
        query_mock.join.assert_called()
        join_mock1.join.assert_called()
        join_mock2.filter.assert_called_with(ClientLoyaltyUsage.client_id == self.client_id)
        filter_mock.all.assert_called_once()
    def test_get_loyalty_empty_raises_exception(self):
        """При отсутствии программ лояльности должно выбрасываться исключение."""
        # Настраиваем запрос так, чтобы метод all() вернул пустой список
        query_mock = MagicMock()
        query_mock.join.return_value.join.return_value.filter.return_value.all.return_value = []
        self.mock_session.query.return_value = query_mock

        with self.assertRaises(HTTPException) as context:
            self.repo.get_loyalty(self.client_id)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Программа лояльности не найдена")

    def test_initialization_with_different_db_sessions(self):
        """Проверка инициализации объекта с разными сессиями базы данных."""
        for _ in range(3):
            fake_session = MagicMock()
            repo = ClientRepository(fake_session)
            self.assertEqual(repo.db, fake_session)

    def test_sequence_update_then_get_by_id(self):
        """Проверка последовательного вызова методов update_client и get_by_id."""
        new_data = DummyData(name="Сергей Сергеев", email="sergey@example.com")
        updated_client = self.repo.update_client(self.client_id, new_data)
        result = self.repo.get_by_id(self.client_id)
        self.assertEqual(updated_client, self.test_client)
        self.assertEqual(result, self.test_client)
        self.assertEqual(self.mock_session.query.call_count, 2)

if __name__ == "__main__":
    unittest.main()