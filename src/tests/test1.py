import unittest
from unittest.mock import MagicMock, patch
import uuid

from src.api.repos.partner_repository import PartnerRepository


# Импортируем тестируемый класс (предполагается, что он находится в файле partner_repository.py)

# Фиктивные классы для моделей (определите или импортируйте реальные модели по необходимости)
class DummyPartner:
    def __init__(self, partner_id):
        self.partner_id = partner_id

class DummyLoyalty:
    def __init__(self, loyalty_id, partner_id, title, target_usages):
        self.loyalty_id = loyalty_id
        self.partner_id = partner_id
        self.title = title
        self.target_usages = target_usages

class DummyClient:
    def __init__(self, client_id):
        self.client_id = client_id

class DummyClientLoyaltyUsage:
    def __init__(self, loyalty_id, client_id, n_count):
        self.loyalty_id = loyalty_id
        self.client_id = client_id
        self.n_count = n_count

class DummyPartnerStatGeneral:
    def __init__(self, partner_id, client_id, loyalty_id, start_loyalty, finish_loyalty, return_loyalty):
        self.partner_id = partner_id
        self.client_id = client_id
        self.loyalty_id = loyalty_id
        self.start_loyalty = start_loyalty
        self.finish_loyalty = finish_loyalty
        self.return_loyalty = return_loyalty

class DummyPartnerStat:
    def __init__(self, partner_id, loyalty_id, date_time, plus_one, give):
        self.partner_id = partner_id
        self.loyalty_id = loyalty_id
        self.date_time = date_time
        self.plus_one = plus_one
        self.give = give


class TestPartnerRepository(unittest.TestCase):
    def setUp(self):
        # Создаем фиктивную сессию БД и экземпляр репозитория
        self.db = MagicMock()
        self.repo = PartnerRepository(self.db)
        self.partner_id = "partner_1"
        self.client_id = "client_1"
        self.loyalty_id = str(uuid.uuid4())
        self.dummy_partner = DummyPartner(self.partner_id)
        self.dummy_loyalty = DummyLoyalty(self.loyalty_id, self.partner_id, "Test Loyalty", 5)
        self.dummy_client = DummyClient(self.client_id)
        self.dummy_client_loyalty_usage = DummyClientLoyaltyUsage(self.loyalty_id, self.client_id, 0)

    def test_get_by_id_found(self):
        # Имитируем возврат партнёра при запросе
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = self.dummy_partner
        self.db.query.return_value = query_mock

        partner = self.repo.get_by_id(self.partner_id)
        self.assertEqual(partner, self.dummy_partner)
        self.db.query.assert_called_once()

    def test_get_by_id_not_found(self):
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = None
        self.db.query.return_value = query_mock

        partner = self.repo.get_by_id("non_existent")
        self.assertIsNone(partner)

    def test_update_partner_success(self):
        # Симулируем, что партнер найден
        self.repo.get_by_id = MagicMock(return_value=self.dummy_partner)
        # data – имитируем объект, у которого метод dict() возвращает словарь обновляемых данных
        data = MagicMock()
        data.dict.return_value = {"title": "Updated Title"}

        result = self.repo.update_partner(self.partner_id, data)
        self.assertEqual(result, self.dummy_partner)
        # Проверяем, что был выполнен запрос на обновление и commit
        self.db.execute.assert_called_once()
        self.db.commit.assert_called_once()

    def test_update_partner_not_found(self):
        self.repo.get_by_id = MagicMock(return_value=None)
        data = MagicMock()
        data.dict.return_value = {"title": "Updated Title"}
        with self.assertRaises(Exception) as context:
            self.repo.update_partner(self.partner_id, data)
        self.assertEqual(str(context.exception), "Partner not found")

    def test_add_loyalty_success(self):
        self.repo.get_by_id = MagicMock(return_value=self.dummy_partner)
        data = {"title": "New Loyalty", "target_usages": 10}
        result = self.repo.add_loyalty(self.partner_id, data)
        self.assertEqual(result["title"], "New Loyalty")
        self.assertEqual(result["target_usages"], 10)
        self.db.add.assert_called_once_with(result)
        self.db.commit.assert_called_once()

    def test_add_loyalty_partner_not_found(self):
        self.repo.get_by_id = MagicMock(return_value=None)
        data = {"title": "New Loyalty", "target_usages": 10}
        with self.assertRaises(Exception) as context:
            self.repo.add_loyalty(self.partner_id, data)
        self.assertEqual(str(context.exception), "Partner not found")

    def test_get_loyalty_with_pagination_success(self):
        # Симулируем, что партнер найден
        self.repo.get_by_id = MagicMock(return_value=self.dummy_partner)
        # Подготавливаем фиктивный объект запроса
        loyalty_instance = self.dummy_loyalty
        query_mock = MagicMock()
        query_mock.filter.return_value = query_mock
        query_mock.count.return_value = 1
        # Для цепочки limit().offset().all() возвращаем список из одного элемента
        query_mock.limit.return_value.offset.return_value.all.return_value = [loyalty_instance]
        self.db.query.return_value = query_mock

        result, total = self.repo.get_loyalty_with_pagination(self.partner_id, limit=10, offset=0)
        self.assertEqual(total, 1)
        self.assertEqual(result[0]["loyalty_id"], str(self.dummy_loyalty.loyalty_id))
        self.assertEqual(result[0]["title"], self.dummy_loyalty.title)
        self.assertEqual(result[0]["target_usages"], self.dummy_loyalty.target_usages)

    def test_get_loyalty_with_pagination_partner_not_found(self):
        self.repo.get_by_id = MagicMock(return_value=None)
        with self.assertRaises(Exception) as context:
            self.repo.get_loyalty_with_pagination(self.partner_id, limit=10, offset=0)
        self.assertEqual(str(context.exception), "Partner not found")

    def test_scan_loyalty_partner_or_client_not_found(self):
        # Симулируем, что партнер не найден
        self.repo.get_by_id = MagicMock(return_value=None)
        with self.assertRaises(Exception) as context:
            self.repo.scan_loyalty(self.partner_id, self.client_id)
        self.assertEqual(str(context.exception), "Not found")

    def test_scan_loyalty_success(self):
        # Симулируем, что и партнер, и клиент найдены
        self.repo.get_by_id = MagicMock(return_value=self.dummy_partner)
        self.repo.get_client_by_id = MagicMock(return_value=self.dummy_client)
        # Так как в исходном коде метод get_client_loyalty возвращает один объект, а затем происходит итерация,
        # для теста мы переопределяем его, чтобы вернуть список (например, список лояльностей)
        dummy_loyalty_iterable = [self.dummy_loyalty]
        self.repo.get_client_loyalty = MagicMock(return_value=dummy_loyalty_iterable)
        # Симулируем, что для каждого элемента (лояльности) клиентская статистика найдена
        self.repo.get_client_loyalty_usage = MagicMock(return_value=self.dummy_client_loyalty_usage)

        result = self.repo.scan_loyalty(self.partner_id, self.client_id)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["title"], self.dummy_loyalty.title)
        # Можно добавить дополнительные проверки структуры результата

    def test_scan_loyalty_plus_one_not_found(self):
        # Если партнер не найден – генерируем исключение
        self.repo.get_by_id = MagicMock(return_value=None)
        with self.assertRaises(Exception) as context:
            self.repo.scan_loyalty_plus_one(self.partner_id, self.client_id, self.loyalty_id)
        self.assertEqual(str(context.exception), "Not found")

    def test_scan_loyalty_plus_one_new_usage(self):
        # Симулируем ситуацию, когда партнер, клиент и лояльность существуют, а записи использования ещё нет
        self.repo.get_by_id = MagicMock(return_value=self.dummy_partner)
        self.repo.get_client_by_id = MagicMock(return_value=self.dummy_client)
        self.repo.get_client_loyalty_by_loyalty = MagicMock(return_value=self.dummy_loyalty)
        # При запросе записи использования возвращаем None
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = None
        self.db.query.return_value = query_mock

        result = self.repo.scan_loyalty_plus_one(self.partner_id, self.client_id, self.loyalty_id)
        self.assertEqual(result, {"status": "ok"})
        self.assertTrue(self.db.add.called)
        self.db.commit.assert_called()

    def test_scan_loyalty_plus_one_max_usage(self):
        # Симулируем ситуацию, когда значение n_count равно target_usages – должно быть исключение
        self.repo.get_by_id = MagicMock(return_value=self.dummy_partner)
        self.repo.get_client_by_id = MagicMock(return_value=self.dummy_client)
        self.repo.get_client_loyalty_by_loyalty = MagicMock(return_value=self.dummy_loyalty)
        # Создаем запись использования, где n_count уже достиг target_usages
        usage = DummyClientLoyaltyUsage(self.loyalty_id, self.client_id, self.dummy_loyalty.target_usages)
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = usage
        self.db.query.return_value = query_mock

        with self.assertRaises(Exception) as context:
            self.repo.scan_loyalty_plus_one(self.partner_id, self.client_id, self.loyalty_id)
        self.assertEqual(str(context.exception), "You cann't do it")

    def test_scan_loyalty_give_not_enough_marks(self):
        # Симулируем ситуацию, когда количество отметок меньше требуемого (target_usages)
        self.repo.get_by_id = MagicMock(return_value=self.dummy_partner)
        self.repo.get_client_by_id = MagicMock(return_value=self.dummy_client)
        self.repo.get_client_loyalty_by_loyalty = MagicMock(return_value=self.dummy_loyalty)
        usage = DummyClientLoyaltyUsage(self.loyalty_id, self.client_id, 3)  # target_usages = 5
        query_mock = MagicMock()
        query_mock.filter.return_value.first.return_value = usage
        self.db.query.return_value = query_mock

        with self.assertRaises(Exception) as context:
            self.repo.scan_loyalty_give(self.partner_id, self.client_id, self.loyalty_id)
        self.assertEqual(str(context.exception), "Client doesn't have enough marks")

    def test_scan_loyalty_give_success(self):
        # Симулируем ситуацию, когда количество отметок равно target_usages
        self.repo.get_by_id = MagicMock(return_value=self.dummy_partner)
        self.repo.get_client_by_id = MagicMock(return_value=self.dummy_client)
        self.repo.get_client_loyalty_by_loyalty = MagicMock(return_value=self.dummy_loyalty)
        usage = DummyClientLoyaltyUsage(self.loyalty_id, self.client_id, self.dummy_loyalty.target_usages)
        query_mock_usage = MagicMock()
        query_mock_usage.filter.return_value.first.return_value = usage
        # Для запроса partner_stat_general возвращаем фиктивный объект
        partner_stat_general = DummyPartnerStatGeneral(self.partner_id, self.client_id, self.loyalty_id, 1, 0, 0)
        query_mock_stat = MagicMock()
        query_mock_stat.filter.return_value.first.return_value = partner_stat_general

        # Используем side_effect, чтобы первый вызов db.query() вернул query_mock_usage, а второй – query_mock_stat
        self.db.query.side_effect = [query_mock_usage, query_mock_stat]

        result = self.repo.scan_loyalty_give(self.partner_id, self.client_id, self.loyalty_id)
        self.assertEqual(result, {"status": "ok"})
        self.assertEqual(usage.n_count, 0)
        self.assertEqual(partner_stat_general.finish_loyalty, 1)
        self.assertTrue(self.db.add.called)
        self.db.commit.assert_called()

if __name__ == '__main__':
    unittest.main()
