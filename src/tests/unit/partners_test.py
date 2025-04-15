from src.api.repos.partner_repository import PartnerRepository
from src.api.services.db_service import Partner

import unittest
from unittest.mock import MagicMock
from fastapi import HTTPException
from datetime import datetime

from src.api.schemas.partner_schemas import PartnerDataUpdate


class TestPartnerRepository(unittest.TestCase):
    def setUp(self):
        # Создаём имитацию сессии базы данных с методами query, add, commit
        self.db = MagicMock()
        # Для метода query настроим цепочку вызовов
        self.query_mock = MagicMock()
        self.db.query.return_value = self.query_mock

        self.repo = PartnerRepository(self.db)

        # Dummy-объект партнёра для тестирования
        self.partner = Partner(partner_id="1", name="Test Partner", email="test@example.com", password_hash="secret")

    def test_get_by_id_success(self):
        # Имитируем, что запрос возвращает партнёра
        self.query_mock.filter.return_value.first.return_value = self.partner

        result = self.repo.get_by_id("1")
        self.assertEqual(result, self.partner)
        self.db.query.assert_called_with(Partner)

    def test_get_by_id_not_found(self):
        # Имитируем отсутствие партнёра (возвращается None)
        self.query_mock.filter.return_value.first.return_value = None

        with self.assertRaises(HTTPException) as context:
            self.repo.get_by_id("non-existent")
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Партнёр не найден")


    def test_update_partner_success(self):
        # Настраиваем запрос так, чтобы get_by_id возвращал существующего партнёра
        self.query_mock.filter.return_value.first.return_value = self.partner
        update_data = {"name": "Updated Name", "email": "updated@example.com"}
        updated_partner = self.repo.update_partner("1", update_data)
        self.assertEqual(updated_partner.name, "Updated Name")
        self.assertEqual(updated_partner.email, "updated@example.com")
        self.db.commit.assert_called()  # проверяем, что commit был вызван


    def test_initialization_with_different_parameters(self):
        # Проверка инициализации с различными параметрами базы данных
        dummy_db = MagicMock()
        repo1 = PartnerRepository(dummy_db)
        self.assertEqual(repo1.db, dummy_db)

        dummy_db2 = MagicMock()
        repo2 = PartnerRepository(dummy_db2)
        self.assertEqual(repo2.db, dummy_db2)


    def test_update_and_get_sequence(self):
        # Настраиваем get_by_id для update_partner и последующего вызова get_by_id
        self.query_mock.filter.return_value.first.return_value = self.partner
        update_data = {"name": "Sequence Name"}
        update_data = PartnerDataUpdate(**update_data)
        updated_partner = self.repo.update_partner("1", update_data)
        print(updated_partner)
        self.assertEqual(updated_partner["name"], "Sequence Name")
        # Последующее получение должно вернуть уже обновлённого партнёра
        partner_after_update = self.repo.get_by_id("1")
        self.assertEqual(partner_after_update.name, "Sequence Name")


    # Дополнительные тесты для методов add_loyalty и get_loyalty_with_pagination можно писать аналогичным образом,
    # моделируя поведение методов add, query.all и пр.

if __name__ == '__main__':
    unittest.main()
