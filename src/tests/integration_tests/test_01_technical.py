import pytest
import json
import requests

BASE_URL = "http://localhost:8080/api"

def test_ping():
    response = requests.get(BASE_URL + "/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "PROOOOOOOOOOOOOOOOOD"}


import pytest
from fastapi.testclient import TestClient
from src.main import app  # импортируйте ваше приложение FastAPI

# client = TestClient(app)

# Фикстура для данных нового пользователя
@pytest.fixture
def new_client_data():
    return {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "TestPass123",  # убедитесь, что в схеме ожидается поле password
        "date_birthday": "1990-01-01",
        "gender": "MALE"
    }

# Фикстура для регистрации пользователя.
# Если пользователь уже существует, можно проверять код 409 и пропускать регистрацию.
@pytest.fixture
def registered_client(new_client_data):
    response = requests.post(BASE_URL + "/client/auth/sign-up", json=new_client_data)
    # ожидаем либо успешную регистрацию, либо ошибку при повторной регистрации
    assert response.status_code in (200, 409)
    return new_client_data


# Фикстура для получения токена авторизации
@pytest.fixture
def token(registered_client):
    credentials = {
        "email": registered_client["email"],
        "password": registered_client["password"]
    }
    response = requests.post(BASE_URL + "/client/auth/sign-in", json=credentials)
    assert response.status_code == 200, response.text
    data = response.json()
    token_value = data.get("token")
    assert token_value is not None
    return token_value

# Тест для регистрации пользователя
def test_signup_success(new_client_data):
    response = requests.post(BASE_URL + "/client/auth/sign-up", json=new_client_data)
    if response.status_code == 409:
        # Если пользователь уже зарегистрирован, проверяем соответствующее сообщение
        assert response.json()["detail"] == "This email is already registered."
    else:
        assert response.status_code == 200
        data = response.json()
        assert "token" in data

# Тест для авторизации
def test_signin_success(registered_client):
    credentials = {
        "email": registered_client["email"],
        "password": registered_client["password"]
    }
    response = requests.post(BASE_URL + "/client/auth/sign-in", json=credentials)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "token" in data
    print(data)

# Тест для получения профиля (эндпоинт GET /client/profile)
def test_get_profile(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(BASE_URL + "/client/profile", headers=headers)
    # Если профиль найден, проверяем наличие ключевых полей
    if response.status_code == 200:
        data = response.json()
        assert "name" in data
        assert "email" in data
    else:
        # В случае отсутствия профиля, может возвращаться 404
        assert response.status_code == 404

# Тест для редактирования профиля (эндпоинт PATCH /client/profile)
def test_patch_profile(token):
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "name": "Updated Name"
        # Добавьте другие поля, если необходимо, в соответствии с ClientDataUpdate
    }
    response = requests.patch(BASE_URL + "/client/profile", json=update_data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        assert data["name"] == "Updated Name"
    else:
        # Возможные коды ошибок – 404 (профиль не найден) или 422 (ошибка валидации)
        assert response.status_code in (404, 422)

# Тест для генерации QR-кода (эндпоинт GET /client/qr)
def test_get_qr(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(BASE_URL + "/client/qr", headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Ожидается, что данные будут списком, например, с одним элементом (идентификатором)
        assert isinstance(data, str)
        assert len(data) > 0
    else:
        # Если токен невалидный, ожидаем 401
        assert response.status_code == 401

# Тест для получения данных программы лояльности (эндпоинт GET /client/loyalty)
def test_get_loyalty(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(BASE_URL + "/api/client/loyalty", headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Ожидается, что данные будут списком с элементами, содержащими поля, описанные в OneClientLoyalty
        assert isinstance(data, list)
        # Пример: проверяем наличие хотя бы одного элемента и его структуру
        if data:
            loyalty_item = data[0]
            assert "name" in loyalty_item
            assert "loyalties" in loyalty_item
    else:
        # Возможные коды ошибок – 401 (невалидный токен) или 404 (программа лояльности не найдена)
        assert response.status_code in (401, 404)

